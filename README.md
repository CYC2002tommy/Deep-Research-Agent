# Deep Research Agent

**Deep Science Writer** is an end-to-end scientific literature skill for Claude Code (Hermes/ECC-compatible). It interviews you until the request is clear, picks a search strategy, decides on its own when abstracts are not enough and the full texts must be read, grounds every claim in a real, resolving DOI, has a strict peer reviewer check everything before delivery, and files the papers and outputs into your knowledge base.

## 🌟 About
A literature pipeline that asks first, measures instead of guessing, and refuses to cite what it cannot verify: Scopus / Exa / OpenAlex / Semantic Scholar / AnySearch retrieval, full-text search over ScienceDirect and Europe PMC, an APA 7th reference table built from DOIs, and a Nature/Science-level review gate.

## 🌟 Key Features

* **It asks before it searches.** Phase 0 is a design-tree interview (the grill-me method): at most five lettered questions per round, each with a recommended answer, so you can reply "Q1 B, Q2 A" or "go with your picks". Facts it can look up, it looks up. Nothing beyond one exploratory search runs until you approve a single blueprint.
* **Three search strategies** (method adapted from the workflows Consensus publishes; no Consensus tool is used):
  * `sub-area`: map a field with PICO / SPIDER / Decomposition, track papers that recur across sub-areas, recurring research groups and citations per year.
  * `facets`: five facet searches, **verbatim gap quotes** grepped from full texts, and a three-paragraph positioning narrative for an Introduction or a proposal.
  * `syllabus`: a course reading list with plain-language summaries and higher-order discussion questions.
* **Stop gates and budgets.** `map` (abstract-level tables), `section` (grounded, humanized prose), or `manuscript` (the whole pipeline to `.docx`); 5, 10 or exhaustive searches; subagents only when you approve them.
* **A measured full-text trigger.** Abstracts rarely say how a method was applied: in one real run, 0 of 121 abstracts mentioned both key terms, and the answer sat in the Methods sections. The OpenAlex harvest counts the abstracts that match every key concept; **fewer than 5 means the full-text search runs**, as do method-detail questions, number-or-mechanism claims and contradictions. `fulltext_search.py` reads up to 30 full texts (Elsevier XML and Europe PMC JATS, kept with their section headings) and extracts the sentences you need.
* **Strict quality control.** Q1-Q2 journals; Q3 only when crucial and marked `[Q3]`; no Q4 and no MDPI.
* **Anti-hallucination.** Every DOI is resolved; every claim is checked against the full text, never the abstract alone; anything from outside the run's searches is labelled `[not from search]`; a thin result is reported with its cause, never passed off as a research gap.
* **A reference table you can trust (`.xlsx`).** Title, authors and the APA 7th citation come from the DOI itself (doi.org content negotiation), never retyped. Wrong DOIs (title mismatch), dead DOIs and duplicates are flagged, and article numbers that citeproc drops are restored.
* **A reviewer gate on every output.** The full `remi` peer-review protocol *(named in tribute to my academic advisor, Remi Chauvy)* is written into the skill and refreshed from the installed `remi` skill before each review. Nothing is delivered while a blocking concern is open. An optional blind second review comes from a different model family.
* **ELI5 summary on request.** At the very end the skill asks whether you want a one-page picture explainer (`懶人包`) built only from the reviewed output.
* **Knowledge loop.** Every downloaded full text and every output can go into an Obsidian vault and a local RAG, with a health check that each note is indexed and retrievable; NotebookLM upload is optional.
* **No bot-detection bypass.** Full texts come from open access (Unpaywall), the Elsevier Article Retrieval API, Europe PMC, or PDFs you download yourself.

---

## 📋 Prerequisites

### 1. System Requirements
* **Claude Code** (or Hermes / a compatible ECC runner).
* **Node.js** v18+ (OpenAlex harvest template, MCP servers).
* **Python 3.10+**.

### 2. Python Dependencies
```bash
pip install python-docx PyMuPDF requests openpyxl matplotlib pandas
```

### 3. MCP Servers
* **Scopus MCP (`scopus-mcp`)**: needs a free Elsevier API key (`SCOPUS_API_KEY`) from the [Elsevier Developer Portal](https://dev.elsevier.com/). The same key powers ScienceDirect full-text search and the Article Retrieval API; full-text access follows your institution's entitlement.
* **Exa Search MCP** (recommended): neural search and open-access discovery.
* **Playwright MCP** (recommended): JavaScript-rendered pages.
* **NotebookLM MCP** (optional): Phase 7 source upload.

### 4. Optional local helpers (used only when installed)
* **obsidian-rag** (a local hybrid-retrieval MCP server) for the RAG ingestion and health check.
* **Gemini CLI custom agents** (`ask-agy.cmd`) as independent reviewers, readers and screeners, and a **local Ollama model** for retrieval-check questions. Without them the skill does that work itself and says so.

### 5. Local Environment
* **Obsidian:** the vault path is set in `SKILL.md` (Phase 7) and `scripts/rag_ingest.py` (`VAULT_ROOT`).
* **Output:** the final `.docx` defaults to the `D:\` drive (change it in `SKILL.md` Phase 6); everything else stays in the run folder.

---

## 🚀 Installation

Clone this repository into your agent's skills directory:

```bash
cd <AGENT_SKILLS_DIR>
git clone https://github.com/CYC2002tommy/Deep-Research-Agent.git
```
*(Replace `<AGENT_SKILLS_DIR>` with your agent's skills path, e.g. `~/.claude/skills/`.)*

---

## 🧠 The Pipeline

1. **Phase 0 (Interview & Blueprint):** grilling rounds, one exploratory search, then one blueprint (strategy, stop gate, budget, sources, helpers) and your single approval.
2. **Phase 0.5 & 1 (Discovery):** multi-source harvest with cross-search tracking, screening, full-text download, and the measured full-text trigger.
3. **Phase 2 (Deep Extraction):** values, mechanisms and verbatim quotes from the full texts.
4. **Phase 3 (Drafting):** evidence-backed outline and APA 7th citations.
5. **Phase 4 & 4.5 (Humanize & Verify):** strip AI fluff; resolve every DOI; ground every claim; replace, never delete, unsupported citations.
6. **Phase 5 (Remi Review):** review-and-revise loop at the `manuscript` gate.
7. **Phase 6 (Compilation):** the `.docx`, only after Phases 4, 4.5 and 5 pass.
8. **Phase 7 (Knowledge Base):** the reference table, then the vault, RAG and NotebookLM.
9. **Phase 8 (Final Remi Check):** every gate's output and the reference table, before delivery.
10. **Phase 9 (懶人包):** an optional ELI5 explainer.

---

## 💻 Usage Example

> *"Use deep-science-writer: has anyone interpolated CASA or GLO-PEM NPP with a thin-plate spline?"*

The agent asks a short round of lettered questions, shows one blueprint, and after your approval runs to the agreed stop gate, here a full-text search, because the question is a method detail.

---

## ⚖️ Academic Ethics & AI Usage Disclaimer

While **Deep Science Writer** implements rigorous anti-hallucination checks, DOI verification, and strict Q1/Q2 filtering, it remains an AI assistant, not an author. By using this tool, you agree to the following principles of academic integrity:

1. **Human Accountability:** The human researcher assumes 100% responsibility for the final manuscript's accuracy, scientific validity, and originality. AI-generated syntheses must be critically reviewed, not blindly accepted.
2. **Evidence Verification:** Though the agent downloads and parses full-text PDFs to prevent hallucination, you must personally verify that the cited literature supports the claims in the exact context you intend. Do not rely solely on the agent's interpretation.
3. **Transparency & Disclosure:** You must comply with your target journal's or institution's policies regarding AI usage. Transparently declare the use of AI tools (e.g., Hermes Agent, LLMs) in the methodology or acknowledgments if required by the publisher.
4. **Originality over Automation:** Using AI is not a violation of ethics if used correctly as a scaffolding tool. True research requires your unique insights, critical thinking, and intellectual contribution. This tool is designed to eliminate tedious formatting and literature gathering, not to bypass the core cognitive work of science.

---
**License:** MIT
