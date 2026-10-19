"""Full-text search: find papers whose *body* says something abstracts do not.

Searches ScienceDirect (Elsevier Search API, Scopus key) and Europe PMC (open access,
no key), fetches up to `max_fulltexts` full texts, and pulls out every sentence that
contains a context term. Built for method-detail questions ("has anyone interpolated
X with a thin-plate spline?"), where the answer sits in a Methods section.

    python fulltext_search.py spec.json OUTDIR

spec.json:
    {"queries": ["\"CASA\" \"thin plate spline\" \"net primary\"", "\"GLO-PEM\" \"spline\""],
     "context_terms": ["spline"],                      # regexes; sentences with any are kept
     "flag_terms": {"casa": "\\bCASA\\b", "glopem": "GLO-?PEM"},   # optional presence flags
     "max_fulltexts": 30,
     "sources": ["sciencedirect", "europepmc"]}

Queries use ScienceDirect syntax (quoted phrases, implicitly AND-ed); for Europe PMC the
phrases are joined with AND and restricted to papers with full text. Writes to OUTDIR:
hits.json (checkpointed after every query), fulltext/<id>.txt, contexts.json, summary.md.
Exits 2 if any search or fetch failed: a failed call is not an empty literature.
"""
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = "deep-science-writer/2.0"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"


def elsevier_key():
    cfg = json.loads(Path("C:/Users/User/.claude.json").read_text(encoding="utf-8"))
    return cfg["mcpServers"]["scopus"]["env"]["SCOPUS_API_KEY"]


def http(url, data=None, method="GET", headers=None, timeout=90):
    req = urllib.request.Request(url, data=data, method=method, headers={"User-Agent": UA, **(headers or {})})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise RuntimeError(f"HTTP {e.code}")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == 2:
                raise RuntimeError(f"network error: {e}")
        time.sleep(3 * (attempt + 1))


def norm_doi(d):
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", (d or "").strip(), flags=re.I).lower()


def search_sd(q, key):
    body = json.dumps({"qs": q, "display": {"show": 100, "sortBy": "relevance"}}).encode()
    d = json.loads(http("https://api.elsevier.com/content/search/sciencedirect", body, "PUT",
                        {"X-ELS-APIKey": key, "Accept": "application/json", "Content-Type": "application/json"}))
    hits = [{"doi": norm_doi(r.get("doi")), "pii": r.get("pii"), "title": r.get("title"),
             "venue": r.get("sourceTitle"), "year": (r.get("publicationDate") or "")[:4]} for r in d.get("results", [])]
    return d.get("resultsFound"), hits


def search_epmc(q):
    phrases = re.findall(r'"([^"]+)"', q) or [q]
    query = " AND ".join(f'"{p}"' for p in phrases) + " AND HAS_FT:Y AND OPEN_ACCESS:Y"
    d = json.loads(http(f"{EPMC}/search?query={urllib.parse.quote(query)}&format=json&pageSize=100&resultType=lite"))
    hits = [{"doi": norm_doi(r.get("doi")), "pmcid": r.get("pmcid"), "title": r.get("title"),
             "venue": r.get("journalTitle"), "year": r.get("pubYear"),
             "authors": [a.strip() for a in (r.get("authorString") or "").rstrip(".").split(",") if a.strip()]}
            for r in d.get("resultList", {}).get("result", [])]   # authors kept: some PMC papers have no DOI
    return d.get("hitCount"), hits


def jats_markdown(xml, rec):
    """Europe PMC JATS -> Markdown: abstract + body with ## section titles, no <front> metadata,
    no reference list, entities decoded. Fills the record's DOI and year from the XML when the
    search result lacked them (resultType=lite omits them for some PMC papers)."""
    if not rec.get("doi"):
        m = re.search(r'<article-id pub-id-type="doi">([^<]+)</article-id>', xml)
        rec["doi"] = norm_doi(m.group(1)) if m else ""
    if not rec.get("year"):
        m = re.search(r"<pub-date[^>]*>.*?<year>(\d{4})</year>", xml, re.S)
        rec["year"] = m.group(1) if m else rec.get("year")

    def md(fragment):
        s = re.sub(r"<title[^>]*>(.*?)</title>", lambda m: f"\n\n## {m.group(1)}\n\n", fragment, flags=re.S)
        s = re.sub(r"</(p|caption|table-wrap)>", "\n\n", s)
        s = html.unescape(re.sub(r"<[^>]+>", " ", s))
        s = re.sub(r"[ \t]+", " ", s)
        return re.sub(r"\n\s*\n\s*", "\n\n", s).strip()

    abstract = re.search(r"<abstract[^>]*>(.*?)</abstract>", xml, re.S)
    body = re.search(r"<body[^>]*>(.*?)</body>", xml, re.S)
    parts = ([f"## Abstract\n\n{md(abstract.group(1))}"] if abstract else []) + ([md(body.group(1))] if body else [])
    return "\n\n".join(parts)


def fetch_text(rec, key, stem):
    """Fetch once, cache the raw API response, convert on every run (so a better converter
    needs no re-download, and a cache hit still fills the DOI and year from the XML)."""
    if rec.get("pmcid"):
        raw_path = stem.with_suffix(".jats.xml")
        if not raw_path.exists():
            raw_path.write_text(http(f"{EPMC}/{rec['pmcid']}/fullTextXML"), encoding="utf-8")
            time.sleep(1)
        return jats_markdown(raw_path.read_text(encoding="utf-8"), rec), "Europe PMC JATS XML"
    ident = f"doi/{rec['doi']}" if rec.get("doi") else f"pii/{rec['pii']}"
    raw_path = stem.with_suffix(".els.xml")
    if not raw_path.exists():
        raw_path.write_text(http(f"https://api.elsevier.com/content/article/{ident}?httpAccept=text/xml",
                                 headers={"X-ELS-APIKey": key, "Accept": "text/xml"}), encoding="utf-8")
        time.sleep(1)
    text = elsevier_markdown(raw_path.read_text(encoding="utf-8"))
    if text:
        return text, "Elsevier Article Retrieval API (XML)"
    plain_path = stem.with_suffix(".els.plain")
    if not plain_path.exists():
        plain_path.write_text(http(f"https://api.elsevier.com/content/article/{ident}?httpAccept=text/plain",
                                   headers={"X-ELS-APIKey": key, "Accept": "text/plain"}), encoding="utf-8")
        time.sleep(1)
    return plain_path.read_text(encoding="utf-8"), "Elsevier Article Retrieval API (text/plain)"


def elsevier_markdown(xml):
    """Elsevier full-text XML -> Markdown with ## section headings and blank-line paragraphs,
    so RAG chunks follow the paper's sections. text/plain is one 80 KB line after ~15 KB of
    asset URLs. Returns "" when the XML has no body sections (abstract-only entitlement)."""
    body = re.search(r"<ce:sections>(.*?)</ce:sections>", xml, re.S)
    if not body:
        return ""
    abstract = re.search(r'<ce:abstract[^>]*class="author"[^>]*>(.*?)</ce:abstract>', xml, re.S) \
        or re.search(r"<ce:abstract[^>]*>(.*?)</ce:abstract>", xml, re.S)

    def md(fragment):
        s = re.sub(r"<ce:section-title[^>]*>(.*?)</ce:section-title>", lambda m: f"\n\n## {m.group(1)}\n\n", fragment, flags=re.S)
        s = re.sub(r"</(ce:para|ce:simple-para|ce:caption)>", "\n\n", s)
        s = re.sub(r"<[^>]+>", " ", s)
        s = re.sub(r"[ \t]+", " ", s)
        return re.sub(r"\n\s*\n\s*", "\n\n", s).strip()

    parts = ([f"## Abstract\n\n{md(re.sub(r'<ce:section-title[^>]*>.*?</ce:section-title>', '', abstract.group(1), flags=re.S))}"]
             if abstract else []) + [md(body.group(1))]
    return "\n\n".join(parts)


def title_found(title, text):
    """Verify by content: most of the title's words must appear near the start of the text."""
    words = [w for w in re.findall(r"[a-z]{4,}", (title or "").lower())]
    head = text[:6000].lower()
    return not words or sum(w in head for w in words) / len(words) >= 0.6


def main(spec_path, outdir):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    out = Path(outdir)
    (out / "fulltext").mkdir(parents=True, exist_ok=True)
    sources = spec.get("sources", ["sciencedirect", "europepmc"])
    key = elsevier_key() if "sciencedirect" in sources else None
    records, log, failed = {}, [], 0

    for q in spec["queries"]:
        for src in sources:
            try:
                found, hits = search_sd(q, key) if src == "sciencedirect" else search_epmc(q)
                mdpi = [h for h in hits if h["doi"].startswith("10.3390")]
                log.append({"query": q, "source": src, "found": found, "returned": len(hits), "mdpi_excluded": len(mdpi)})
                for h in hits:
                    if h["doi"].startswith("10.3390"):
                        continue
                    k = h["doi"] or h.get("pii") or h.get("pmcid")
                    rec = records.setdefault(k, {**h, "sources": [], "queries": []})
                    rec["pmcid"] = rec.get("pmcid") or h.get("pmcid")
                    rec["sources"] = sorted(set(rec["sources"]) | {src})
                    rec["queries"] = sorted(set(rec["queries"]) | {q})
            except RuntimeError as e:
                failed += 1
                log.append({"query": q, "source": src, "error": str(e)})
            (out / "hits.json").write_text(json.dumps({"log": log, "records": records}, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"{src:13} {log[-1].get('found', 'ERR')!s:>6} {q}")
            time.sleep(1)

    year = lambda r: int(r["year"]) if str(r.get("year") or "").isdigit() else 0
    ranked = sorted(records.values(), key=lambda r: (-len(r["queries"]), -year(r)))   # most queries hit, then newest
    for term in [*spec.get("context_terms", []), *spec.get("flag_terms", {}).values()]:
        if re.search(r"[\x00-\x1f]", term):   # "\b" written with one backslash in JSON is a backspace
            sys.exit(f"spec regex {term!r} holds a control character: write \\\\b, not \\b, in JSON")
    ctx_re = re.compile("|".join(spec.get("context_terms", [])) or r"$^", re.I)
    flags = {k: re.compile(v, re.I) for k, v in spec.get("flag_terms", {}).items()}
    contexts = {}
    for rec in ranked[: spec.get("max_fulltexts", 30)]:
        ident = rec["doi"] or rec.get("pii") or rec.get("pmcid")
        stem = out / "fulltext" / re.sub(r"[^a-z0-9]+", "_", ident.lower())
        cache = stem.with_suffix(".md")   # the converted text: this file is what rag_ingest.py stores
        try:
            raw, source = fetch_text(rec, key, stem)
            if rec["doi"].startswith("10.3390"):   # a PMC paper whose DOI only showed up in its XML
                continue
            cache.write_text(raw, encoding="utf-8")
            text = re.sub(r"\s+", " ", raw)
            sents = re.split(r"(?<=[.;])\s+(?=[A-Z(])", text)
            entry = {"title": rec["title"], "doi": rec["doi"], "pmcid": rec.get("pmcid"), "text_path": str(cache),
                     "source": source,
                     "venue": rec["venue"], "journal": rec["venue"], "year": rec["year"], "authors": rec.get("authors", []),
                     "sources": rec["sources"], "queries": rec["queries"], "chars": len(text),
                     "content_check": "ok" if title_found(rec["title"], text) else "TITLE NOT FOUND IN TEXT",
                     "flags": {k: bool(r.search(text)) for k, r in flags.items()},
                     "contexts": [s[:400] for s in sents if ctx_re.search(s)][:8]}
            if len(text) < 3000:
                entry["content_check"] = "SHORT TEXT: probably abstract only, not full text"
        except RuntimeError as e:
            failed += 1
            entry = {"title": rec["title"], "doi": rec["doi"], "error": str(e)}
        contexts[ident] = entry
        (out / "contexts.json").write_text(json.dumps(contexts, ensure_ascii=False, indent=1), encoding="utf-8")

    cell = lambda s: re.sub(r"\s+", " ", str(s if s is not None else "")).replace("|", "/")
    lines = ["# Full-text search summary", "",
             f"Unique papers: {len(records)}. Full texts read: {sum('chars' in c for c in contexts.values())}. "
             f"With a context sentence: {sum(bool(c.get('contexts')) for c in contexts.values())}. Failed calls: {failed}.", "",
             "| Source | Query | Found | Returned | MDPI excluded | Error |", "|---|---|---|---|---|---|"]
    lines += [f"| {l['source']} | {cell(l['query'])} | {l.get('found', '')} | {l.get('returned', '')} | {l.get('mdpi_excluded', '')} | {cell(l.get('error'))} |" for l in log]
    lines += ["", "## Papers read (context sentences)", ""]
    for c in contexts.values():
        lines.append(f"### {cell(c['title'])} ({c.get('year', '')}) {c.get('doi') or ''}")
        lines.append(f"- check: {c.get('content_check', c.get('error'))}; flags: {c.get('flags', {})}")
        lines += [f"  - {cell(s)}" for s in c.get("contexts", [])]
    (out / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(records)} papers, {len(contexts)} read, {failed} failed -> {out / 'summary.md'}")
    return 2 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
