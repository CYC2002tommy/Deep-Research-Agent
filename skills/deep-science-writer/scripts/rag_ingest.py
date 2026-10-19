"""Put downloaded full texts, and the run's outputs, into the Obsidian vault and obsidian-rag.

    python rag_ingest.py texts.json "<topic>" [--index]     # full texts -> Hermes/raw/papers/<topic>/
    python rag_ingest.py --index-only "<vault-relative folder>"   # e.g. Hermes/artifacts/literature/<date>_<topic>

texts.json is fulltext_search.py's contexts.json or fetch_oa_fulltexts.py's manifest as is
(entries that failed their download check are refused), or a hand-made list:
    [{"doi": "10.1016/j.jag.2023.103638", "text_path": "run/fulltext/x.txt",
      "source": "Elsevier Article Retrieval API (XML)", "title": "<expected title, optional>",
      "tags": ["NPP", "CASA"]}]

Each full text becomes Hermes/raw/papers/<topic>/<FirstAuthor>_<Year>_<ShortTitle>.md with YAML
front matter. Title, authors, year and journal come from the DOI (doi.org CSL-JSON), never
retyped. A text is refused when the DOI's title is not found near the start of the text
(wrong file), when the expected title does not match the DOI, or when it is under 3,000
characters (an abstract, not a full text). A DOI already under raw/papers is skipped.

--index / --index-only: unload the local model (it shares the GPU with the embedder), run
obsidian-rag's incremental `index` (whole vault, so removed notes are pruned) and `embed`, then
scripts/rag_check.py: the health gate, plus advisory findability for papers (not for the run's
outputs). A retry re-checks notes already in the topic folder. Needs obsidian-rag registered in
~/.claude.json; otherwise the notes are written and the indexing step is reported as skipped.

The last stdout line is JSON. Exit 2 if an entry failed to ingest or a note failed the health
gate; downloads that failed their own check are listed as "refused_upstream" and do not count.
Full texts stay in the private vault; never commit them to a repo.
"""
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # the Windows console is cp950 here
sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_reference_table import CSL, authors_of, fetch, first, norm_doi, plain, similar  # noqa: E402

VAULT = Path(os.environ.get("VAULT_ROOT", "C:/Users/User/Documents/Obsidian Vault"))
PAPERS = VAULT / "Hermes" / "raw" / "papers"
CHECK = Path(__file__).resolve().parent / "rag_check.py"


def rag_python():
    """The obsidian-rag interpreter, read from its MCP registration (no hard-coded path)."""
    try:
        cfg = json.loads((Path.home() / ".claude.json").read_text(encoding="utf-8"))
        return cfg["mcpServers"]["obsidian-rag"]["command"]
    except (OSError, KeyError, ValueError):
        return None


def existing_ids():
    """DOI or PMCID -> note. A note with a YAML `doi:` key is taken at its word (even when
    empty). Older notes without the key: a doi.org link in the first 1,500 characters (the
    header), never a Crossref Funder Registry DOI (10.13039/...), which JATS front matter carries."""
    seen = {}
    for md in PAPERS.rglob("*.md"):
        head = md.read_text(encoding="utf-8", errors="replace")[:1500]
        key = re.search(r'^doi:\s*"?([^"\s]*)"?\s*$', head, re.M)
        if key:
            doi = key.group(1)
        else:
            links = [d for d in re.findall(r"doi\.org/(10\.\d{4,9}/[^\s\"<>)\]]+)", head) if not d.startswith("10.13039")]
            doi = links[0] if links else ""
        if doi:
            seen[norm_doi(doi).rstrip(".")] = md
        pmc = re.search(r'^pmcid:\s*"?(PMC\d+)"?\s*$', head, re.M)
        if pmc:
            seen[pmc.group(1).upper()] = md
    return seen


def title_in_text(title, text):
    words = re.findall(r"[a-z]{4,}", plain(title).lower())
    head = re.sub(r"\s+", " ", text[:8000]).lower()
    return not words or sum(w in head for w in words) / len(words) >= 0.6


def slug(s, n, min_len=3):
    words = [w for w in re.findall(r"[A-Za-z0-9]+", s) if len(w) >= min_len][:n]
    return "_".join(w.capitalize() for w in words) or "Untitled"


def yaml_value(v):
    return json.dumps(v, ensure_ascii=False)   # a JSON string is a valid YAML double-quoted scalar


class Refused(Exception):
    """Refused upstream: the download itself failed its check. Reported, not an ingest error."""


def write_note(e, folder, cache, seen):
    doi = norm_doi(e.get("doi"))
    if e.get("error") or e.get("content_check", "ok") != "ok":
        raise Refused(e.get("error") or e["content_check"])
    pmc = (e.get("pmcid") or "").upper()
    for ident in (doi, pmc):
        if ident and ident in seen:
            return None, str(seen[ident])
    text = Path(e["text_path"]).read_text(encoding="utf-8", errors="replace")
    if len(text) < 3000:
        raise RuntimeError(f"text is {len(text)} characters: an abstract, not a full text")
    meta = json.loads(fetch(doi, CSL, cache)) if doi else {}
    title = plain(first(meta.get("title"))) or e.get("title", "Untitled")
    if e.get("title") and doi and similar(e["title"], title) < 0.6:
        raise RuntimeError(f"expected title does not match the DOI's title '{title[:80]}'")
    if not title_in_text(title, text):
        raise RuntimeError(f"the DOI's title '{title[:80]}' is not near the start of the text: wrong file?")
    authors = [a.strip() for a in authors_of(meta).split(";") if a.strip()] or e.get("authors") or []
    year = (meta.get("issued", {}).get("date-parts") or [[None]])[0][0] or e.get("year")
    first_author = authors[0] if authors else "Anon"
    # "Family, Given" (from the DOI) or Europe PMC's "Family Initials" ("Ma Q")
    family = (meta.get("author") or [{}])[0].get("family") or \
        (first_author.split(",")[0] if "," in first_author else first_author.split()[0])
    name = f"{slug(family, 1, min_len=1)}_{year or 'nd'}_{slug(title, 5)}.md"   # Li, Xu, Wu are real surnames
    path = folder / name
    if path.exists():
        path = folder / name.replace(".md", f"_{re.sub(r'[^a-z0-9]', '', doi)[-6:]}.md")
    fm = {"title": title, "type": "raw", "authors": authors, "year": year,
          "journal": plain(first(meta.get("container-title"))) or e.get("journal") or e.get("venue") or "",
          "doi": doi, "pmcid": e.get("pmcid") or "", "source": e.get("source", ""),
          "retrieved": datetime.date.today().isoformat(), "tags": ["paper", *e.get("tags", [])]}
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            lines.append(f"{k}:" if v else f"{k}: []")
            lines += [f"  - {yaml_value(x)}" for x in v]
        else:
            lines.append(f"{k}: {yaml_value(v) if isinstance(v, str) else (v if v is not None else '')}")
    lines += ["---", "", f"# {title}", "",
              f"{'; '.join(authors)} · *{fm['journal']}* ({year}) · DOI: {doi}", "",
              f"> Full text retrieved {fm['retrieved']} via {fm['source']}. Source material, not the user's notes.", "",
              text]
    path.write_text("\n".join(lines), encoding="utf-8")
    for ident in (doi, pmc):
        if ident:
            seen[ident] = path
    return str(path), None


def unload_local_model():
    body = json.dumps({"model": "gemma4:12b", "keep_alive": 0}).encode()
    req = urllib.request.Request("http://localhost:11434/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=60).read()
    except OSError:
        pass


def index_and_check(notes, questions=2):
    """Incremental index of the whole vault, embed, then the health gate. Returns (log, failed?).
    Not `index --paths`: that skips pruning, so a note removed or renamed inside the folder
    would stay live and searchable. A whole-vault incremental index took 8 s (789 notes)."""
    py = rag_python()
    if not py:
        return {"index": "skipped: obsidian-rag is not registered in ~/.claude.json"}, False
    repo = Path(py).resolve().parents[2]   # <repo>/.venv/Scripts/python.exe; the CLI reads <repo>/obsidian-rag.toml
    unload_local_model()
    log = {}
    for args in (["index"], ["embed"]):
        r = subprocess.run([py, "-m", "obsidian_rag.cli", *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=repo)
        log[args[0]] = f"exit {r.returncode}: {(r.stdout + r.stderr)[-600:]}"
        if r.returncode:
            return log, True
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump({"written": notes}, f)
        tmp = f.name
    r = subprocess.run([py, str(CHECK), tmp, "--questions", str(questions)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=repo)
    Path(tmp).unlink(missing_ok=True)
    print(r.stdout[:-1] if r.stdout.endswith("\n") else r.stdout)
    try:
        log["check"] = json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        log["check"] = f"rag_check.py exit {r.returncode}: {r.stderr[-600:]}"
    return log, r.returncode != 0


def main(argv):
    if argv[:1] == ["--index-only"] and len(argv) == 2:
        folder = VAULT / argv[1]
        notes = [str(p) for p in folder.rglob("*.md")]
        log, bad = index_and_check(notes, questions=0)   # run outputs: the health gate only
        print(json.dumps({"indexed": notes, "log": log}, ensure_ascii=False))
        return 2 if bad else 0
    args = [a for a in argv if a != "--index"]
    if len(args) != 2:
        sys.exit(__doc__)
    src, topic = args
    data = json.loads(Path(src).read_text(encoding="utf-8"))
    entries = list(data.values()) if isinstance(data, dict) else data
    folder = PAPERS / re.sub(r'[<>:"/\\|?*]', "-", topic).strip()
    folder.mkdir(parents=True, exist_ok=True)
    cache = Path(src).resolve().parent / ".doi_cache"
    cache.mkdir(exist_ok=True)
    seen = existing_ids()
    written, skipped, refused, failed = [], [], [], []
    for e in entries:
        try:
            path, existing = write_note(e, folder, cache, seen)
            (written.append(path) if path else skipped.append({"doi": norm_doi(e.get("doi")), "note": existing}))
        except Refused as why:
            refused.append({"doi": norm_doi(e.get("doi")), "reason": str(why)})
        except (RuntimeError, OSError, KeyError, ValueError) as err:
            failed.append({"doi": norm_doi(e.get("doi")), "text_path": e.get("text_path"), "error": str(err)})
    log, bad = ({}, False)
    # also re-check notes skipped inside this folder, so a retry after an interrupted index/embed completes
    here = [s["note"] for s in skipped if Path(s["note"]).resolve().parent == folder.resolve()]
    if "--index" in argv and (written or here):
        log, bad = index_and_check(written + here)
    print(json.dumps({"written": written, "skipped": skipped, "refused_upstream": refused, "failed": failed,
                      "log": log}, ensure_ascii=False))
    return 2 if failed or bad else 0   # a refused download is reported, not an ingest failure


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
