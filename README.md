# Deep Research Agent

**Deep Science Writer** is an industrial-grade, end-to-end scientific research pipeline and AI agent skill. Designed for the Hermes/ECC framework, it completely automates the literature review process: from background full-text database querying down to anti-hallucination verification, Nature/Science-level peer review, `.docx` compilation, and Obsidian/NotebookLM knowledge base ingestion.

## 🌟 About
An autonomous AI agent pipeline for rigorous academic research, featuring strict DOI verification, multi-agent Scopus/OpenAlex/Semantic Scholar retrieval, and APA 7th `.docx` generation.

## 🌟 Key Features

* **Precision Background Sourcing (Two-Stage Pipeline):** Subagents first fetch and screen a large pool of abstracts (e.g., 100+). For the highly relevant subset, the agent downloads and deeply reads the *full text* (Methodology, Results) to prevent abstract-induced hallucination. **FULL-TEXT verification of final claims is absolutely mandatory.**
* **Strict Quality Control:** Explicitly targets Q1-Q2 journals. Marks Q3 when strictly necessary. **Bans all Q4 and MDPI publications.**
* **Multi-Agent Discovery:** Spawns exactly three concurrent subagents to query Scopus, Exa, OpenAlex, and Semantic Scholar simultaneously for exhaustive mapping.
* **Strict Compliance:** The agent is hard-coded to strictly follow every step in order. Skipping phases or taking shortcuts (like drafting without full-text verification) is strictly forbidden.
* **Zero-Hallucination Guarantee (Phase 4.5):** Automatically runs live HTTP `requests` tests against every generated DOI to ensure 100% validity. Cross-references generated claims against raw full texts to prevent AI overstatement.
* **Automated Peer Review:** Integrates the `remi` peer-review skill *(named in tribute to my academic advisor, Remi Chauvy)* to aggressively strip "AI fluff" (e.g., "delve", "tapestry") and enforce rigorous academic tone.
* **English Output Only:** Enforces strict English language generation for all academic reports and drafts, regardless of conversational language.
* **Hands-Free Output:** Programmatically builds a fully formatted Microsoft Word document (`.docx`) with APA 7th hanging indents and auto-generated data visualizations.
* **Knowledge Management Loop:** Automatically saves research summaries to your local **Obsidian Vault** and explicitly uploads **every individually cited reference** as a separate source into **Google NotebookLM** for precise audio overviews and cross-referencing.

---

## 📋 Prerequisites

To run this skill successfully, your host environment must be configured with the following dependencies and Model Context Protocol (MCP) servers:

### 1. System Requirements
* **Hermes Agent** (or a compatible ECC/Claude Code runner).
* **Node.js** (v18+ recommended) and `npx` for running MCP servers.
* **Python 3.10+** (in your system PATH or agent's virtual environment).

### 2. Python Dependencies
The agent relies on Python to generate documents and verify links.
```bash
pip install python-docx PyMuPDF requests matplotlib seaborn pandas
```

### 3. Required MCP Servers
Add these to your `config.yaml` or `claude_desktop_config.json`:

* **Scopus MCP (`scopus-mcp`)**
  * Required for premium literature retrieval.
  * **API Key:** Requires a free Elsevier Scopus API Key (`SCOPUS_API_KEY`). Apply at the [Elsevier Developer Portal](https://dev.elsevier.com/).
* **NotebookLM MCP (`notebooklm-mcp-server`)**
  * Required for Phase 7 knowledge ingestion.
  * **Auth:** Must run `npx notebooklm-mcp-server auth` once in your terminal to authenticate your Google Account locally.
* **Exa Search MCP** (Highly Recommended)
  * Used for neural search fallback and broad open-access discovery.
* **GitHub MCP & Playwright MCP** (Optional but recommended for broader functionality).

### 4. Local Environment
* **Obsidian:** The skill looks for `%OBSIDIAN_VAULT_PATH%\Hermes\` (fallback: `%USERPROFILE%\Documents\Obsidian Vault\Hermes\`). Update `SKILL.md` Phase 7 or set the environment variable if your vault is located elsewhere.
* **Output Drive:** All outputs strictly save to `D:\Tommy` (or your configured environment).

---

## 🚀 Installation

Clone this repository into your agent's skills directory:

```bash
cd <AGENT_SKILLS_DIR>
git clone https://github.com/CYC2002tommy/Deep-Research-Agent.git
```
*(Replace `<AGENT_SKILLS_DIR>` with your agent's skills path, e.g., `~/.hermes/skills/` or `.agents/skills/` for the ECC framework).*

---

## 🧠 The 7-Phase Architecture

1. **Phase 0 and 0.5 (Plan & Background Execution):** The agent formulates a search plan and halts for your explicit approval. Once approved, it launches a local background process (`terminal(background=true)`) to scrape the full text of exactly 30 high-impact papers via APIs.
2. **Phase 1 (Strict Multi-Agent Discovery):** Deploys exactly three concurrent subagents utilizing `scopus-mcp`, `exa-search`, OpenAlex, and Semantic Scholar. Enforces journal quality limits (Q1-Q2 only, bans MDPI).
3. **Phase 2 (Deep Extraction):** Consolidates metadata, full texts, and key findings.
4. **Phase 3 (Structural Drafting):** Outlines the article with evidence-backed claims and APA 7th citations.
5. **Phase 4 and 4.5 (Anti-Hallucination):** Strips AI vocabulary. Pings all DOIs to ensure they resolve (404 = citation deleted).
6. **Phase 5 (Remi Review):** An internal peer-review loop that critiques and rewrites the draft until academic standards are met. *(Named in tribute to my academic advisor, Remi Chauvy).* 
7. **Phase 6 (Compilation):** Python scripts draw Mermaid/Matplotlib charts and compile the final `.docx` (ONLY allowed after Phase 4, 4.5, and 5 are passed).
8. **Phase 7 (Knowledge Graph):** Updates Obsidian and pushes papers to NotebookLM.

---

## 💻 Usage Example

Simply trigger the agent with a research prompt:

> *"Please use the deep-science-writer skill to research the sociological and psychological acceptance of sustainability policies, segmented by age (public) and firm size (SMEs vs Large Enterprises)."*

The agent will take over, present a blueprint, ask for your approval, and then execute the entire pipeline autonomously.

---
**License:** MIT
