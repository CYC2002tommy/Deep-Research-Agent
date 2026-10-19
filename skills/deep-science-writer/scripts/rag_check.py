"""Check that notes just written to the vault are really in obsidian-rag, and how findable they are.

Run with the obsidian-rag interpreter (rag_ingest.py does this for you):
    <rag python> rag_check.py notes.json [--questions 2] [-k 10]

notes.json: {"written": ["C:/.../Hermes/raw/papers/<topic>/X.md", ...]}  (rag_ingest.py's result)

1. Health, deterministic, the gate: each note is in the index, not quarantined, has chunks,
   and every chunk has a vector. A failure is a broken ingest: hand it to rag-admin.
2. Findability, advisory: the local model writes `--questions` paraphrased questions per note
   from its indexed chunks (agy-helpers ask_local.py --job eval-questions). The local model is
   then unloaded, BGE-M3 and the reranker load once, and every question is searched over the
   whole vault. The note's best rank is reported. A miss is usually other papers on the same
   topic ranking higher, not a broken ingest, so it is reported, not escalated.

Exit 2 if any note fails health; findability never changes the exit code.
"""
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # the Windows console is cp950 here
ASK_LOCAL = Path("C:/Users/User/AppData/Local/agy-helpers/ask_local.py")
LOCAL_MODEL = "gemma4:12b"


def unload_local_model():
    """The local model and the embedder share one GPU; free it before BGE-M3 loads."""
    body = json.dumps({"model": LOCAL_MODEL, "keep_alive": 0}).encode()
    req = urllib.request.Request("http://localhost:11434/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=60).read()
    except OSError:
        pass   # Ollama not running: nothing to unload


def ask_question(chunk):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(chunk)
        tmp = f.name
    try:
        r = subprocess.run([sys.executable, str(ASK_LOCAL), "--job", "eval-questions", "--input", tmp],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    except subprocess.TimeoutExpired:
        return ""
    finally:
        Path(tmp).unlink(missing_ok=True)
    for line in reversed(r.stdout.strip().splitlines()):
        try:
            return (json.loads(line).get("question") or "").strip()
        except (ValueError, AttributeError):
            continue
    return ""


def main(src, n_questions, k):
    try:
        from obsidian_rag.cli import _backends, _load
        from obsidian_rag.retrieve.pipeline import search
        from obsidian_rag.store.sqlite_store import Store
    except ImportError:
        print("skipped: run this with the obsidian-rag interpreter")
        return 0
    notes = json.loads(Path(src).read_text(encoding="utf-8")).get("written", [])
    cfg = _load(None, None)
    report, broken = [], 0
    with Store(cfg.storage_path() / "index.sqlite3") as store:
        db = store.db
        root = Path(cfg.vault.path).resolve()
        for path in notes:
            # the indexer keys notes by the NFC vault-relative path, case-folded (path_fold)
            rel = unicodedata.normalize("NFC", Path(path).resolve().relative_to(root).as_posix())
            row = db.execute("SELECT note_id, rel_path, trust FROM notes WHERE deleted_at IS NULL AND path_fold = ?",
                             (rel.casefold(),)).fetchone()
            if not row:
                report.append({"note": rel, "health": "NOT INDEXED"})
                broken += 1
                continue
            chunks = db.execute("SELECT chunk_id, raw_text, row FROM chunks WHERE note_id = ? AND deleted_at IS NULL "
                                "ORDER BY chunk_id", (row["note_id"],)).fetchall()
            problems = []
            if row["trust"] == "quarantined":
                problems.append("QUARANTINED (not searchable)")
            if not chunks:
                problems.append("NO CHUNKS")
            missing = sum(c["row"] is None for c in chunks)
            if missing:
                problems.append(f"{missing} of {len(chunks)} chunks have no vector (run embed)")
            broken += bool(problems)
            body = [c for c in chunks if 300 <= len(c["raw_text"] or "") <= 2500
                    and not re.match(r"\s*(references|bibliography)\b", c["raw_text"], re.I)]
            mid = body[len(body) // 4: max(len(body) // 4 + 1, len(body) * 3 // 4)] or body
            step = max(1, len(mid) // max(1, n_questions))
            report.append({"note": row["rel_path"], "trust": row["trust"], "chunks": len(chunks),
                           "health": "; ".join(problems) or "ok",
                           "sample": [c["raw_text"] for c in mid[::step][:n_questions]]})

    if n_questions == 0:   # health gate only (the run's outputs): no local model, no embedder
        for r in report:
            r.pop("sample", None)
            r["findability"] = "skipped"
            print(f"{r['health'][:40]:40} {'skipped':24} {r['note']}")
        print(json.dumps({"notes": len(report), "health_failures": broken, "results": report}, ensure_ascii=False))
        return 2 if broken else 0

    for r in report:   # all local-model calls first, then free the GPU once
        r["questions"] = [q for q in (ask_question(t) for t in r.pop("sample", [])) if q]
    unload_local_model()

    embedder, dense, reranker = _backends(cfg, want_embed=True, want_rerank=cfg.rerank.enabled)
    with Store(cfg.storage_path() / "index.sqlite3") as store:
        for r in report:
            ranks = []
            for q in r.get("questions", []):
                res = search(store, [q], embedder=embedder, dense=dense, reranker=reranker, top_k=k,
                             candidates=cfg.retrieve.candidates_per_channel, rrf_c=cfg.retrieve.rrf_c,
                             fusion=cfg.retrieve.fusion, alpha=cfg.retrieve.alpha,
                             max_per_note=cfg.retrieve.max_per_note, mode="hybrid")
                paths = [h.rel_path for h in res.hits]
                ranks.append(paths.index(r["note"]) + 1 if r["note"] in paths else None)
            r["question_ranks"] = list(zip(r.get("questions", []), ranks))
            found = [x for x in ranks if x]
            r["findability"] = ("untested" if not ranks else f"best rank {min(found)} of top {k}" if found
                                else f"not in top {k} (advisory)")
            print(f"{r['health'][:40]:40} {r['findability']:24} {r['note']}")
    print(json.dumps({"notes": len(report), "health_failures": broken, "results": report}, ensure_ascii=False))
    return 2 if broken else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    nq = int(a[a.index("--questions") + 1]) if "--questions" in a else 2
    kk = int(a[a.index("-k") + 1]) if "-k" in a else 10
    sys.exit(main(a[0], nq, kk))
