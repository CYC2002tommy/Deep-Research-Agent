---
name: deep-science-writer
description: "Scientific literature pipeline on Scopus, Exa, OpenAlex, Semantic Scholar and AnySearch: map a field (themes, foundational papers, research groups, gaps), find verbatim gap quotes and draft a positioning narrative for an Introduction or proposal, build a course reading list from a syllabus, or run the full manuscript pipeline with full-text verification, humanization and Remi peer review. Use when the user asks to find literature, review a field, back a claim with references, identify a research gap, or write a scientific article."
---

# Deep Science Writer (End-to-End Pipeline)

This skill orchestrates a multi-stage pipeline for scientific research, combining neural search, browser automation, academic synthesis, and humanized writing. It merges the capabilities of Exa Search, Playwright, Google Science Skills, Deep Research, and Text Humanization into one cohesive workflow.

## 🎯 Trigger Conditions
- User asks to write a scientific article, literature review, or deep-dive research report.
- User asks to "find literature for X", map a field, locate a research gap, back an Introduction or proposal with references, or turn a syllabus into a reading list (see the strategies in Phase 0 step 4).
- User requests comprehensive research using web searching and scraping (Exa + Playwright).
- The output requires rigorous academic citations (APA 7th) but a highly natural, human-like reading flow.

## 📋 Workflow Steps

### Phase 0: Mandatory Deep Context Gathering & Research Plan
1. Incorporate academic rigor, structured literature parsing, and cross-validation techniques into your approach and keep those principles active in context. Reference material for these lives in the local repos `C:/Users/User/workspace/nature-skills/`, `C:/Users/User/workspace/academic-research-skills/`, and `C:/Users/User/workspace/superpowers/` — these are **not** installed skills, so read from them with `Read`/`Grep` rather than trying to invoke them.
2. **Mandatory Grilling (user's rule, 2026-10-19):** You MUST interview the user until every decision below is settled, and run nothing past RECON (step 3) before then. The grilling (grill-me) method is written out here in full, so it runs where the grilling skill is not installed:
   - **Design tree.** Map the request as a tree: every decision branches into the decisions that hang off it.
   - **Rounds and the frontier.** The frontier is every decision whose prerequisites are already settled: the questions you can ask now without guessing at answers you have not heard yet. Ask the frontier in one round, then wait for the user's answers before the next round. A question whose answer depends on another question still open in this round belongs to a later round, not this one.
   - **Recompute after every round.** Each round of answers reshapes the tree: settled decisions push the frontier outward and unblock the questions that depended on them. Recompute the frontier and ask the next round.
   - **Format.** At most 5 questions per round; the rest of the frontier waits for the next round. Number them Q1, Q2, …, give lettered options and your recommended answer, in the user's language, so the user can reply "Q1 B, Q2 A" or "全部照建議". Keep every answer to a letter or a few words; never make an answer depend on writing a paragraph.

     ```
     ❓ **Q1** - **<title>**: <question> A) … B) … C) …
     ➡️ <recommended letter + one-line reason>
     ```
   - **Facts are your job, decisions are the user's.** Before each round, read what the request points at (the manuscript, its reference list, vault notes, memory, project files) inline. Never ask the user for something you can look up; ask only what is theirs to decide. Do not block on a lookup: one still running is an unsettled prerequisite, so only the questions downstream of it wait; ask the rest of the frontier now. A branch the prompt or memory already settles is pre-settled: state it in the blueprint instead of asking it.
   - **The tree** (a branch opens once its parent is settled; a branch whose condition does not hold is skipped):

     | Branch | Settles | Ask when |
     |---|---|---|
     | Purpose | what the literature is for: a manuscript section, a proposal, a reviewer reply, a course, understanding a field | always |
     | Scope | the question's boundaries: mechanisms, region, scale, period, and what is explicitly out | always |
     | Deliverable | the stop gate; edit the user's document directly or write a separate report; output language; length budget | always |
     | Full-text route | open access and the Elsevier API only, or also papers the user downloads by hand (how many) | gate `section` or `manuscript` |
     | Existing references | keep or replace each specific MDPI / Q3 / Q4 reference that an inline scan of the user's draft found | the run edits a draft that has such references |
     | If the literature disagrees | adjust the text only, adjust the analysis too, or report and stop; if the analysis changes, existing data only or new data too; what happens if a conclusion flips | the run tests an existing draft, claim or analysis |

     Round 1, alongside RECON, asks this tree. Strategy, budget, subagent count, strategy details (framework and sub-areas, the five facets, the section grouping) and optional phases need RECON, so they are not separate rounds: the blueprint (step 4) proposes them as lettered choices with recommendations, and the one reply that approves the blueprint settles them too.
   - **Done when the frontier is empty**: every branch answered by the user, pre-settled, skipped by its condition, or explicitly handed back. "你決定" or "照你想法" accepts your recommended answers; list each one as an assumption in the blueprint. Nothing is silently assumed. Do not act on it until the user confirms you have reached a shared understanding: here, that confirmation is the blueprint approval (step 5).
3. **RECON:** run one broad search on the topic as stated (OpenAlex or Scopus) alongside the first grilling round; it needs only the topic. It teaches the vocabulary, themes, method families and high-citation papers that the strategy questions need. Select nothing yet.
4. **Blueprint.** Assembled from the grilling answers: one plan, one approval, and the "shared understanding" check that ends the grilling. It states:
   - **Run rules**: every grilling answer (scope, deliverable, output language, full-text route, reference decisions, the disagreement rule), each pre-settled branch, and each "你決定" assumption, labelled as such. These rules govern the run: where a later phase of this skill says otherwise about full-text sources or output language, the blueprint wins.
   - **Search strategy**, from `references/research-workflows.md`:

     | Strategy | Use when | Procedure |
     |---|---|---|
     | `sub-area` | what a literature says, who works on it, where the gaps are | §1: framework (PICO / SPIDER / Decomposition) and 4-5 sub-areas |
     | `facets` | an Introduction, a proposal's significance and innovation, "has anyone done X" | §2: five facet searches, verbatim gap quotes, positioning narrative |
     | `syllabus` | course topics to a reading list for students | §3: sections, 1-3 papers each, summaries, discussion questions |

   - **Stop gate**: `map` runs the searches and screening (Phase 0.5 step 1, Phase 1) and stops after the abstract-level synthesis tables or reading list and the vault note; `section` runs through Phase 4.5 (full text, drafting, humanizer, grounding) and leaves the Remi review to Phase 8; `manuscript` runs every phase. A positioning narrative or any prose the user will paste into a document needs `section` or higher, so it is humanized and grounded. **Every gate ends with Phase 7 step 3 (reference table, `.xlsx`), Phase 8 (final Remi check), and the Phase 9 question (懶人包 by the eli5 method).**
   - **Budget tier**: `quick` (5 searches), `standard` (10, allocation in §1), or `exhaustive` (the Phase 1 five-source sweep).
   - **Source floor**: `quick` and `standard` use at least two sources, one of them AnySearch `academic.citation` on the seed DOIs; `exhaustive` uses all five.
   - **Subagent count**: default 0. Harvest with the background template (`templates/fetch_openalex_background.js`) and MCP calls in the main conversation. A count above 0 must be named here and approved.
   - **Optional phases** (`manuscript` only): Zotero (4.6), `.docx` with infographics (6), NotebookLM (7.2), each on or off.
5. **Halt & Wait:** You MUST wait for the user's "Explicit Approval" of the blueprint. The grilling rounds and this approval all come before any work; after approval there is no further halt: run to the stop gate and deliver one review package.

The method behind the three strategies is adapted from three workflows Consensus published (consensus.app/home/mcp, read 2026-10-19). Only the method was taken; **the Consensus MCP is not used** (the user declined it). The shared rules in §0 of that file apply in every strategy: provenance labels, sparse is not a gap, cross-search tracking, the search summary.

### Phase 0.5: Background Sourcing, Full-Text Deep Reading, & Gap Analysis
1. **Large-Scale Abstract Screening:** Phases 0.5 and 1 are one discovery stage, not two passes: the abstract pool (e.g., 100+ papers) is the output of the Phase 1 searches, harvested with `templates/fetch_openalex_background.js` in the background plus the MCP sources. Screen these abstracts for strict relevance and Q1/Q2 quality first.
2. **Targeted Full-Text Downloading:** Once the abstracts are verified to match the research need, the script MUST download or scrape the *entire full text* of the filtered subset (e.g., top 20-30 papers).
3. **Deep Reading & Filtering:** Read the downloaded full texts (specifically Methodology and Results) to extract the actual mechanisms. Discard any papers that fail to substantiate the claims in their abstracts or overstate findings.
4. **Long-Running Execution:** Execute the script with the `Bash` tool using `run_in_background: true`. You are re-invoked automatically when it exits — do not poll. Wait for that notification before proceeding.
5. **Mandatory Justification & Gap Report:** Before synthesis or drafting, you MUST write a structured evaluation report containing exactly these three sections. It goes into the deliverable; it is not a second halt.
   - **Selection Rationale (為什麼讀這幾篇)**: Explicitly explain how these specific papers map precisely to the user's stated topic and pain points.
   - **Research Gap (研究缺口在哪)**: Identify what these papers leave unsolved or unaddressed, defining the exact gap in the current literature. Back each gap with a verbatim gap quote (`references/research-workflows.md` §2 step 3) grepped from a downloaded full text, and class it methodological, population/context, or conceptual. A gap with no quote is labelled as your inference.
   - **Topic Enhancement (對課題有什麼提升)**: Clearly articulate how these findings can be fed back into the user's project to improve their experimental design, strengthen their argument, or correct their research trajectory.
6. **Synthesis & Synthesis Mastery:** Merge and critically analyze the findings into a formal academic synthesis report, in the main conversation unless the blueprint approved a subagent for it. *(Note: Override the user's general chat preference for concise lists; use standard formal academic prose here.)*

### Phase 1: Strict Multi-Source Discovery (`scopus-mcp` + `exa-search` + `openalex` + `semantic-scholar` + `anysearch`)
1. **Journal Quality Filter**: ONLY include Q1 and Q2 papers. If a Q3 paper provides crucial evidence, you MUST explicitly mark it in the text/table with `[Q3]`. STRICTLY EXCLUDE any Q4 papers and ANY papers published by MDPI.
2. **Source coverage, not subagent count**: coverage is set by the blueprint's budget tier and source floor (Phase 0 step 4). The five sources below are Source 1 (Scopus), Source 2 (Exa Search), Source 3 (OpenAlex), Source 4 (Semantic Scholar) and Source 5 (AnySearch vertical academic search and citation graph). Run them from the main conversation by default; split them across subagents only when the blueprint names the count and the user approved it.
3. **Exclusion Rules**: Every source, and every subagent if any, MUST strictly adhere to the MDPI/Q4 exclusion rules.
4. **Exhaustive Tier Toolset**: The `exhaustive` tier MUST explicitly utilize ALL of the following databases:
   - `scopus-mcp` (for Elsevier/authoritative DB)
   - `exa-search` (for neural web search and Open Access discovery)
   - OpenAlex API (via Python/Node.js scripts, strictly filtering out MDPI)
   - Semantic Scholar API (via Python/Node.js scripts)
   - AnySearch vertical academic search (via the `anysearch` skill CLI -- see Source 5 below)
   In the `exhaustive` tier, failure to use all five sources is a violation of this skill.
5. **Source 5 -- AnySearch (vertical academic + citation graph).** Installed at `C:/Users/User/.claude/skills/anysearch/`. Runs a bundled CLI against public HTTP endpoints; no MCP server, and **no API key required** (anonymous access works; a key only raises rate limits).

   Its distinct value is the `academic` vertical domain, which the other four cannot match on cost or reliability:

   | sub_domain | Use for |
   |---|---|
   | `academic.citation` | **Citation graph by DOI.** `op=citations` (cited-by), `op=references` (full reference list with DOIs), `op=citation-count`, `op=author`. The highest-value call in this phase. |
   | `academic.search` | Cross-discipline paper search by keyword, title, author, institution; returns metadata and open-access links |
   | `academic.preprint` | arXiv / bioRxiv / medRxiv preprints, with `field`, `year_from`/`year_to`, `open_access`, and direct `doi` lookup |
   | `academic.biomedical` | MEDLINE / PMC with MeSH terms and PMC full-text links |
   | `academic.dataset` | Zenodo / Dryad / Figshare datasets and research software |

   **Always call `get_sub_domains --domain academic` first** to confirm the current parameter set, then search. `id` is a required parameter for `academic.citation`; pass the bare DOI with no `doi:` prefix.

   ```bash
   PY="C:/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/python"
   CLI="C:/Users/User/.claude/skills/anysearch/scripts/anysearch_cli.py"
   "$PY" "$CLI" get_sub_domains --domain academic
   "$PY" "$CLI" search "<DOI>" --tag academic.citation --params "id=<DOI>,op=references" --max_results 10
   "$PY" "$CLI" batch_search --query "topic A" --query "topic B" --tag academic.search --max_results 5
   "$PY" "$CLI" extract --url "<url>"
   ```

   **Why this source exists.** In the 2026-08 Fukuoka run the Semantic Scholar citation-graph track burned roughly 25 minutes against the rate-limited anonymous pool and initially reported a false negative. The same query through AnySearch returned a complete 64-entry reference list with DOIs in about one second, with no key. Assign Source 5 the citation-graph work explicitly: pull `references` and `citations` for every seed DOI, because that is where thematically disconnected literatures surface -- keyword search cannot reach a body of work that shares no vocabulary with the query.

   **Two cautions.** AnySearch *general* web search returns MDPI, ResearchGate, and forum results, so the MDPI/Q4 exclusion must still be applied downstream -- it is not filtered at source. And prefer the vertical `academic.*` tags over plain `search` for literature work; plain web search returns blog-grade results.

6. **Exhaustive Mapping (User Rule)**: Do NOT sample (e.g., just looking at 5 out of 20). Process the *exhaustive* set of relevant findings into a structured Markdown table: `| Title | Authors/Year | Key Finding | URL/DOI |`.
7. **Track across searches** (`references/research-workflows.md` §0-§1): dedupe by DOI and record which sub-areas each paper was hit in, recurring authors, and citations per year; the OpenAlex template computes all three. Allocate a `standard` budget as §1 gives it: sub-area searches, two systematic-review/meta-analysis searches (query terms plus `type:article|review`, because many meta-analyses are indexed as `article`), an era-gated pair to catch terminology shifts, and AnySearch `academic.citation` on the top seed DOIs. End with the search summary; report a thin sub-area with the source's cap or error, never as a gap on its own.

### Phase 2: Deep Extraction (`cloakbrowser` + `deep-research`)
1. **Dynamic Scraping**: For high-value sources that require JavaScript rendering, interaction, or are heavily dynamically loaded, use the **CloakBrowser** tool/CLI to navigate, bypass anti-bot protections, wait for specific DOM selectors, and extract the full text. Do NOT use standard Playwright for this, as CloakBrowser is the primary scraper.
2. **Synthesis**: Cross-reference extracted findings across multiple sources to validate claims and identify consensus vs. controversy. 

### Phase 3: Structural Drafting (`article-writing`)
1. Load the article-writing skill via the `Skill` tool with `skill: "hermes-research:article-writing"`, then outline the article on its principles: strong hook, logical progression, evidence-backed claims, and clear logical headings.
2. Integrate data explicitly. Use block equations or Mermaid diagrams if explaining complex systems or workflows.
3. Format all inline citations and the final reference list strictly in **APA 7th** format. When generating via `python-docx`, programmatically implement APA hanging indents (`p.paragraph_format.first_line_indent = Inches(-0.5)` and `p.paragraph_format.left_indent = Inches(0.5)`) and ensure journal/book titles and volume numbers are properly italicized.

### Phase 4: Humanization & Polish (`text-humanizer`)
1. Load the text-humanizer skill via the `Skill` tool with `skill: "hermes-research:text-humanizer"`, then review the generated draft and ruthlessly strip AI-isms, applying the strict **"No Fluff"** style profile.
2. **Banned AI Vocabulary**: "delve", "tapestry", "in conclusion", "crucial", "testament", "realm", "fosters", "underscores", "moreover".
3. **Style Adjustments**: 
   - Use varied sentence lengths (short, punchy sentences mixed with complex ones).
   - Prefer active voice over passive voice.
   - Remove introductory meta-commentary ("Here is the article...").
   - Ensure the prose flows like a subject-matter expert speaking directly to a peer.

### Phase 4.5: Anti-Hallucination & Evidence Verification
**Strict Requirement:** This phase MUST be completed before Remi (Phase 5) is allowed to review the manuscript.
1. **Extraction**: Scan the draft and extract every single in-text citation (e.g., Smith, 2024) and its corresponding Reference List entry.
2. **DOI/URL Liveness Test**: Use the `Bash` tool (via `curl -I`), Exa Search MCP, or a Python script (e.g., `requests.get` / `urllib`) to ping every DOI or URL in the reference list. For bulk or programmatic URL resolution when links are missing, execute `scripts/verify_urls.py` (uses `ddgs` and `requests`).
   - **STRICT REPLACEMENT RULE**: If a DOI/URL is dead (404) or fake, you MUST NOT simply delete the sentence or claim. You MUST trigger a targeted secondary search (Exa/Scopus) to find a real Q1/Q2 replacement paper that supports the exact claim. Download the new full-text, verify it, and insert the new citation.
3. **Claim Grounding Check**: Cross-reference the specific claims made in the draft against the raw data/abstracts collected in Phases 1 & 2. 
   - **Strict Literalism (就事論事)**: Never over-extend findings. If a claim overstates the actual findings, down-modulate it. 
   - **No Concept Stitching**: Do not stitch a macro/global finding (e.g., "planetary boundaries") with a localized context (e.g., "European summer extremes") in the same citation unless the source explicitly connects them. Stick strictly to the literal facts. If a study analyzes a broad region (e.g., "global temperate drylands"), do not misattribute its specific localized mechanism to a single city (e.g., "Paris") just because that city sits within the region.
- **Differentiate Plant Functional Types (PFTs)**: When interpreting drought resilience, strictly differentiate between shallow-rooted ground vegetation (grass) and deep-rooted urban trees. Do not mistakenly apply a "plant shutdown" mechanism to trees if the literature explicitly states only the ground vegetation was affected due to shallow soil moisture depletion.
4. **Continuous Replacement Loop**: Repeat the search, replacement, and verification process until **EVERY single factual statement or claim in the manuscript is backed by a verified, live reference**.
5. **Pass Condition**: Zero dead links, zero fake DOIs, zero ungrounded claims, and 100% of claims supported by valid references. Only then proceed to Phase 5.

### Phase 4.6: Zotero Archiving & PDF Download
**Strict Requirement (when the blueprint turns Zotero on):** This phase bridges verified evidence with bibliography management before Remi's review.
1. **PDF Retrieval & Anti-Bot Bypass**: For every paper successfully verified in Phase 4.5, you MUST download the original Publisher PDF to the local `assets/` directory.
   - **Step 1 (Open Access)**: Attempt fast retrieval via `scripts/fetch_oa_fulltexts.py` (Unpaywall API).
   - **Step 2 (Paywall/Cloudflare Bypass)**: If Paywalled or blocked by 403/Cloudflare (e.g., Wiley, Elsevier), you MUST execute a Python script utilizing `cloakbrowser` (`launch_context_async`) to navigate to the DOI landing page or PDF direct link. `cloakbrowser` will natively bypass bot protection by leveraging the user's University IP environment and stealth fingerprints. 
2. **Zotero Ingestion (via `pyzotero`)**: 
   - Load the pyzotero skill via the `Skill` tool with `skill: "hermes-research:pyzotero"` to integrate with the Zotero v3 API.
   - For each verified paper, create a Parent Item in Zotero (e.g., `journalArticle`) populated with title, authors, year, DOI, and URL.
3. **PDF Attachment**:
   - Use `zot.attachment_simple([local_pdf_path], parentid=parent_key)` to upload the downloaded PDF as an attachment to its respective Zotero Parent Item.
4. **Error Handling**: If a PDF cannot be downloaded due to aggressive Paywalls, log the failure but still create the Parent Item in Zotero with the DOI/URL to ensure the bibliography record exists.

### Phase 5: Peer Review & Iteration (`remi`)
1. Review as Remi, a strict Nature/Science-level peer reviewer, by the full protocol in `references/remi.md`, refreshed from the installed Remi skill first (Phase 8 step 1 gives the command).
2. Submit the Phase 4 draft to Remi for a rigorous evaluation against evidence backing, APA 7th formatting, logical flow, and academic tone.
3. **Iteration Loop (No-Lazy-Editing Rule)**: Analyze Remi's (or the user's) critique. If structural gaps, missing evidence, or logical errors are found, you are STRICTLY FORBIDDEN from simply deleting the problematic text or rewording it to sound better.
4. **Mandatory Secondary Search**: For any substantive critique or missing evidence, you MUST regress to Phase 1/2, conduct a new targeted literature search to find missing evidence, download the new papers, and rewrite the section based on the newly acquired data.
5. Repeat the Remi review process until Remi approves the manuscript with zero critical concerns.

### Phase 6: Data Visualization & Final Document Generation (.docx)
**CRITICAL RULE**: You MUST NOT generate or export the final .docx file until Phase 4 (Text Humanizer), Phase 4.5 (DOI Verification), and Phase 5 (Remi Review) have been explicitly executed and passed. Skipping these steps before exporting is a strict violation of this pipeline.
1. **Infographic & Statistical Plotting**: 
   - For highly engaging, data-driven storytelling and statistical plots, you MUST utilize the **AntV Infographic** (`@antv/infographic`) framework. 
   - Write a short Node.js/HTML script that uses the AntV declarative infographic syntax to render the key research takeaways or statistics.
   - Use `playwright-mcp` or a local headless browser script to take a high-quality screenshot (`.png`) of the rendered AntV infographic. Save it to `assets/`.
   - You may still use `mermaid.ink` for simple flowcharts, but all major data visualizations should leverage the AntV infographic capabilities for professional aesthetics.
2. **Document Compilation (`docx` or `python-docx`)**: At the `manuscript` stop gate you MUST NOT just output Markdown as the final product. Write a Python script using `python-docx` to programmatically build the final Word document. *Important Windows Environment Note*: When executing the Python script via `Bash`, use absolute paths with forward slashes and enclose them in quotes (e.g., `python "C:/path/to/generate_docx.py"`) to prevent MSYS bash from stripping backslashes and causing `[Errno 2] No such file or directory`.
3. **Embed Assets**: Insert the generated AntV Infographic images and any Mermaid charts into the `.docx` file at the appropriate logical sections. Ensure formatting aligns with APA 7th standards (e.g., proper figure captions).
4. **Final Delivery**: Save the generated `.docx` file directly to the `D:\` drive (e.g., `D:\Research_Report.docx`). Deliver this absolute D:\ path to the user only after Phase 8 has passed, together with the reference table and Remi's report.

### Phase 7: Knowledge Base & NotebookLM Integration
**Order:** step 3 (reference table) runs first, before Phase 8, so Remi checks it. Steps 1 and 2 run only after Phase 8 has passed, so the vault and NotebookLM never receive claims or references that Remi's loop later changes.
1. **Obsidian Wiki Update**: Synthesize the core findings, literature insights, and strategic takeaways. Write or append this synthesis directly into the user's Obsidian Vault (`C:\Users\User\Documents\Obsidian Vault\`) to maintain an ongoing, centralized knowledge base.
2. **NotebookLM Source Ingestion** (when the blueprint turns it on): Utilize the `notebooklm` MCP tools to create a dedicated notebook for this research project. You MUST explicitly upload **every single cited reference** as an **individual source** into NotebookLM (do not just upload one compiled document). Upload the raw abstracts or full-texts for each cited paper so NotebookLM can accurately cross-reference and map individual citations.
3. **Reference table (`.xlsx`) — every run, every gate.** One row per paper the deliverable cites or selects (evidence table, Start-here list, sub-area key papers, reading list, manuscript references). Columns: Title, Authors, DOI, APA 7th citation, Summary, Summary basis, Check.
   - Write `papers.json`: per paper the DOI, the title you expect, a 1-3 sentence summary of what the paper did and found (numbers only if they are in the basis you read), and the basis (`full text` or `abstract`). Summaries are in the blueprint's output language.
   - Run `"C:/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/python" "<skill>/scripts/export_reference_table.py" papers.json "<deliverable folder>/<name>_references.xlsx"`. Use that interpreter: it has `openpyxl`; the skill's own `.venv` does not, and `py` is not installed. Title, authors and the APA citation come from the DOI (doi.org content negotiation), never retyped; the script adds `Article <number>` where citeproc drops it.
   - Exit 2 means a flagged row. `TITLE MISMATCH` means the DOI is wrong: find the right one. `DOI did not resolve` falls under the Phase 4.5 replacement rule. A `single page` flag is settled in `papers.json` with `"article_number": "<n>"` or `"single_page": true` after checking the publisher page. Re-run until the only flags left are deliberate no-DOI sources (grey literature), each one explained in the delivery note.
   - Save it beside the main deliverable.

### Phase 8: Final Remi Check — every run, every gate
**Strict Requirement:** nothing is delivered until Remi has checked everything this run produced: the deliverable at its stop gate and the reference table. This is an internal loop, not a user halt.
1. **Use the latest Remi.** Its full protocol is written into this skill as `references/remi.md`, a byte-for-byte copy of the Remi skill. Where the Remi skill is installed it is the source of truth, so refresh the copy first:

   ```bash
   LIVE="C:/Users/User/.claude/skills/hermes-research/skills/remi/SKILL.md"
   COPY="<skill>/references/remi.md"
   if [ -f "$LIVE" ] && ! cmp -s "$LIVE" "$COPY"; then cp "$LIVE" "$COPY" && echo "remi copy refreshed from the installed skill"; fi
   ```
   Then `Read` `references/remi.md` in full and review by it. Where the Remi skill is not installed (the public mirror), the copy is the protocol. Never review from memory, and never from the mirror's `skills/remi/SKILL.md` or the `learned/` copy, which are older versions. Commit a refreshed copy with the run's other skill changes.
2. **What Remi brings** (orientation only; `references/remi.md` governs):
   - Core red lines: no fabricated citations (suggest searches, never invent entries); support the author's thinking, do not replace it; review section by section when the text is long; unpublished text stays local and is never sent to an external service.
   - Step 0, the causal-chain audit: research question → design → sample → method → analysis → interpretation → conclusions → title; does each link follow? Then construct validity: is every compared category actually measured?
   - Concern format: a stable ID, a verbatim quote (or `location not found`), the issue, and a concrete Required revision.
   - Severity: `SUBMISSION BLOCKER` and `CRITICAL` (= `Blocking: Yes`), `MAJOR`, `PRESENTATION`.
   - Report: Format A (full structured review with verdict, chain diagnosis, numbered Major Issues, equation-by-equation pass, bookkeeping, overclaim rewrite, order of operations, criterion table, decision) or Format B (severity-tagged punch list).
3. **Scope by gate:**

   | Gate | Format | Remi checks |
   |---|---|---|
   | `map` | B | red lines; every claim and gap traceable to a returned record; gaps carry a gap quote or an inference label; no sparse sub-area called a gap; Major Issues 1 (concept precision), 3 (boundaries), 14 (speculation) and 17 (overclaim) applied to the map's statements; bookkeeping sweep; the reference table. For `syllabus` the gap checks are replaced by: each summary says only what its record says, and each discussion question asks students to apply, analyse or evaluate, not recall |
   | `section` | B | all of the above, plus Step 0 on the section's argument and every Major Issue that applies to it; if the run edited a `.docx`, export it to PDF and look at the changed pages |
   | `manuscript` | A | the final `.docx` as rendered (export to PDF and look), every Phase 5 concern confirmed closed, the full protocol, and the reference table |

   In every gate the reference table check is: each row's DOI resolves to its title, the Check column is empty or explained, each summary says only what its basis supports, and the table lists exactly the papers the deliverable cites.
4. **Loop:** any `SUBMISSION BLOCKER` or `CRITICAL` is fixed under the No-Lazy-Editing rule (Phase 5 steps 3-4: a new search and new evidence, not deletion or rewording), the affected outputs are regenerated (the reference table too), and Remi checks again. Done when no blocking concern is left.
5. **Deliver** Remi's final report beside the deliverable. List the remaining `MAJOR` and `PRESENTATION` items in the delivery note, so the user sees what was not fixed.

### Phase 9: Offer a 懶人包 — every run, last message
After delivery and after Phase 7 steps 1-2, the run's very last message asks one question, in the user's language and lettered like the grilling rounds:

```
❓ 要不要懶人包？ A) 要 B) 不用
```

1. **B, or no answer:** the run ends.
2. **A:** build the 懶人包 with the eli5 method. Where the `eli5` skill is installed, load it with the `Skill` tool (`skill: "eli5"`) and pass the brief below as `args`; either way follow the method written here, so the result is the same where eli5 is missing (the public mirror has no eli5 skill).
   - **The brief**, built only from the delivered, Remi-checked outputs: the topic in one line; the 3-5 main findings and the main gap, each with the hedge the deliverable gives it; the deliverable's file paths.
   - **eli5's instruction**: explain it to someone who knows nothing about the topic, as an HTML artifact with big pictures and few words.
   - **Audience**: knows nothing about the field. Explain each idea by its mechanism first (what pushes what, what moves where, and why), then give the term.
   - **Big pictures, few words**: 4-6 panels, one idea per panel. Each panel is a large inline SVG diagram carrying the idea, with a caption of at most two short sentences. Numbers appear only as the deliverable gives them.
   - **Panel order**: what was asked → what the literature shows (the 3-5 findings) → what is still unknown (the main gap) → what it means for the user's work → where the full files are.
   - **Format**: an HTML Artifact; load the `artifact-design` skill first, as the Artifact tool requires. Where no Artifact tool exists, write a standalone `.html` beside the deliverable.
   - **Language**: the user's language unless they ask otherwise.
3. **Nothing new enters the 懶人包.** It restates the deliverable: no claim, number or citation that is not in it, and no hedge dropped for the sake of simplicity (Remi Major Issue 17, overclaim, still applies). Before it is published, check each statement against the deliverable. Because it adds nothing, it needs no second Phase 8 pass.

## 📚 Linked References
- `references/python-docx-manipulation.md`: Patterns for reading, creating, and safely removing XML paragraphs from `.docx` files.
- `references/academic-api-patterns.md`: Reliable curl and Python patterns for hitting Crossref and OpenAlex APIs, including critical URL-encoding fixes.
- `scripts/verify_urls.py`: Python script utilizing `ddgs` and `requests` to programmatically search and verify evidence URLs for Phase 4.5.
- `references/remi.md`: The full Remi review protocol (red lines, causal-chain audit, concern format, Major Issues 1-17, equation pass, bookkeeping, Formats A and B, severity tags), a byte copy of the Remi skill refreshed before each review (Phase 8 step 1).
- `references/research-workflows.md`: The three search strategies (`sub-area`, `facets`, `syllabus`), their shared rules, the budget allocation, the gap-phrase list and the filter mapping for OpenAlex, Scopus and Semantic Scholar.
- `scripts/node/fetch_unpaywall_oa.js`: Resolves DOI to Open Access PDF URLs via Unpaywall.
- `scripts/node/scrape_html_fulltext.js`: Scrapes HTML full texts to bypass basic PDF blocks.
- `scripts/node/extract_pdf_text.js`: PDF parsing script template using `pdf-parse`.
- `scripts/node/generate_docx.js`: Programmatically generates APA 7th compliant DOCX using the `docx` library.
- `templates/fetch_openalex_background.js`: Node.js harvest template for OpenAlex: per-query filters (era gates, `type:article|review`), MDPI exclusion with counts, a checkpoint and a response cache after every query, cross-search tracking (sub-area hits, foundational flag, citations per year, recurring authors) and a search-summary table. Exits 2 if any search failed.
- `scripts/export_reference_table.py`: Writes the Phase 7 step 3 reference table (`.xlsx`) from a JSON list of DOIs and summaries; resolves title, authors and APA 7th from the DOI, flags wrong, dead and duplicate DOIs, exits 2 on any flag.
- `scripts/fetch_oa_fulltexts.py`: Python script utilizing the Unpaywall API and PyMuPDF to automatically locate, download, and extract text from Open Access PDFs for a given list of DOIs. Crucial for Phase 0.5.

## ⚠️ Pitfalls & Strict Rules

- **Zotero Credentials & Setup:** Phase 4.6 relies on the `pyzotero` client. The pipeline will crash or fail to archive if the required environment variables (`ZOTERO_API_KEY`, `ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE`) are missing. Always verify these are present in the environment or a `.env` file before executing the pipeline. **CRITICAL:** `ZOTERO_LIBRARY_ID` MUST be the integer ID (e.g., `16500033`), NOT the username. If the user provides a string username, resolve it programmatically via `GET https://api.zotero.org/keys/<API_KEY>` (`r.json()['userID']`).
- **Unpaywall API Email Requirement:** When querying the Unpaywall API to find Open Access PDFs, you MUST append a valid email parameter (`?email=...`) or the request will fail with HTTP 422.
- **STRICT COMPLIANCE REQUIRED:** You MUST strictly follow EVERY step of every phase the approved blueprint's stop gate and toggles include, in order. Skipping included phases, ignoring instructions, or taking shortcuts (such as writing drafts without full-text verification) is strictly forbidden. There are no exceptions.
- **English Output ONLY:** All generated drafts, reports, and final documents MUST be written strictly in English, regardless of the conversational language, unless the blueprint's output language says otherwise (e.g. the run edits a document written in another language).
- **No bot-detection bypass (precedence over the CloakBrowser lines below):** Claude Code does not bypass Cloudflare, CAPTCHAs or other anti-bot protection, so it never runs the CloakBrowser stealth routes in this file. Its full-text route is the blueprint's: open access (Unpaywall), the Elsevier Article Retrieval API, Europe PMC, then the papers the user downloads by hand. A paper none of these reaches is dropped or put on the user's download list. The CloakBrowser instructions stay for agents whose rules allow them.
- **FULL-TEXT READING IS MANDATORY (NO ABSTRACT-ONLY SHORTCUTS):** You MUST NOT rely solely on abstracts for anything that carries weight: a mechanism, a load-bearing number, a gap quote, or a claim in prose. You MUST download, scrape, or extract the *entire full text* of those papers before synthesizing or extracting mechanisms. If full text is inaccessible, you MUST drop the paper or ask the user for help. DO NOT proceed to drafting based only on OpenAlex/Scopus abstracts. Abstracts and metadata are enough only for screening, for the `map` gate's overview tables (themes, groups, timeline, reading order), and for `syllabus` reading-list summaries; label those tables abstract-level.
- **No Hallucinated Citations:** Every claim MUST map to a real URL/DOI found during Phase 1/2. Anything from memory or outside knowledge is labelled `[not from search]` and never counts toward an evidence table, a gap, or a reading list.
- **Strict Literalism vs. Concept Stitching (Scale & Region Mismatch):** NEVER map physiological/mechanistic findings from one geographical study to an unrelated region, OR from a macro-biome scale to a specific city. If a study covers "Global Temperate Drylands", do NOT explicitly attribute its findings to the urban environment of "Paris" (Geographical Over-Extrapolation). If you lack city-specific data, explicitly run an additional targeted search instead of concept-stitching macro data to fit the prompt. Read and report the literal findings.
- **Cherry-Picking and Data Reversal (PFT Conflation):** Do not ignore the primary conclusion of a paper to isolate a minor variable that fits a preconceived narrative. Pay extreme attention to contrasting functional types within a paper: if a study finds that shallow-rooted *grasses* suffer severe drought stress while deep-rooted *trees* remain resilient, do not conflate the two and falsely claim the trees are suffering (Plant Functional Type Conflation). Read the nuances of the data.
- **MDPI Exclusion & 403 Errors:** MDPI servers (DOI prefix `10.3390`) aggressively block headless requests (curl/node), resulting in 403 Forbidden errors during Phase 4.5 URL verification. Do NOT just fetch them and fail later. When writing the Phase 0.5 background fetch script (e.g., using OpenAlex), **programmatically filter out MDPI** by checking `host_organization_name` (must not include "mdpi") and `doi` (must not include "10.3390") *before* processing or presenting the results to the user.
- **Paywalled Literature (Wiley/Elsevier) & Cloudflare:** Standard APIs and basic Playwright scripts will be blocked by Cloudflare (403 Forbidden / Captcha) on major publisher sites. You MUST write your extraction scripts using `cloakbrowser` (`from cloakbrowser import launch_context_async`) which provides native stealth bypassing. This perfectly synergizes with the user's University IP to unlock full-texts seamlessly.
- **Zotero Metadata Retrieval:** When writing the Zotero archiving script, always fetch the most accurate metadata (Authors, Journal Name, Date) from the Crossref API (`https://api.crossref.org/works/{doi}`) before creating the `pyzotero` Parent Item.
- **Action Over Planning:** Once the Phase 0 blueprint is approved, do not tell the user what you *will* do. Immediately start executing the searches.
- **Table First:** Always build and present the literature/evidence table *before* writing the final prose.
- **Intersection of Zero (Query Formulation):** When cross-analyzing highly specific variables (e.g., comparing 4 distinct cities simultaneously), NEVER combine them into a single academic API search query (e.g., Crossref/Semantic Scholar). This yields zero results. Deconstruct the research into atomic, independent searches (e.g., "Paris drought NPP", "Singapore UHI NPP") and synthesize the results post-retrieval.
- **API Rate Limits & Terminal Environments:** For the Semantic Scholar subagent, you MUST use the dedicated API key stored in the environment variable `SEMANTIC_SCHOLAR_API_KEY`. Include it in the Python/Node.js script's request headers as `{'x-api-key': os.environ.get('SEMANTIC_SCHOLAR_API_KEY')}` to bypass public rate limits and achieve high-throughput retrieval. For Scopus API, complex nested boolean logic with `NOT` may throw `400 Bad Request`; fetch broader results and filter locally via Python. On Windows hosts, the `Bash` tool runs MSYS bash. Always use `python -m pip install` and execute absolute paths using forward slashes and quotes (e.g., `python "C:/path/to/script.py"`) to prevent backslashes from being stripped by the shell. Additionally, when passing absolute Windows paths to python commands, MSYS bash may strip the backslashes causing `[Errno 2] No such file or directory`. Always use forward slashes for paths in terminal execution.
- **OpenAlex Strict Filtering:** When querying the OpenAlex API via custom scripts, you MUST programmatically exclude MDPI and low-tier publishers by strictly checking the `host_organization_name` field (e.g., rejecting "Multidisciplinary Digital Publishing Institute" or "MDPI").
- **Windows MSYS Execution Context:** On Windows hosts, the `Bash` tool runs MSYS bash where standard `python` and `pip` commands may fail or open the Windows Store. On this machine (checked 2026-10-19) `py` is not installed and `python` on PATH is the hermes-agent venv (`C:/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/python`), which has `openpyxl`; call that path explicitly in scripts the skill runs, and install with `<that python> -m pip install`. For background async tasks and PDF extraction, Node.js (`node`) is heavily preferred as it natively handles async loops well in the MSYS terminal without alias issues. See `references/nodejs-pdf-extraction.md` for stable `pdf-parse` templates.
- **Terminal `input()` EOFError:** Do NOT use Python's `input()` function to pause for manual user interaction in scripts executed via the `Bash` tool. The MSYS terminal is non-interactive and will throw `EOFError: EOF when reading a line`. Use `time.sleep()` with a generous buffer instead.
- **Aggressive Cloudflare (Wiley/AGU):** Standard headless `playwright`, `cloudscraper`, and `playwright-stealth` will fail (403 Forbidden or Timeout) against strict publishers like Wiley. You MUST use `cloakbrowser` via Python (`launch_context_async`). If still blocked, fallback to `headless=False` with `asyncio.sleep(15)` to allow the user to manually solve the Captcha visibly before the automated download resumes.
- **Visible Background Agents (Desktop UI vs scheduled runs):** If the user asks to "see" subagents working in the Desktop UI (e.g. for scheduled tracking), do NOT schedule a silent background run — scheduled runs execute headless and are invisible in the UI. Instead, use the `schedule` skill to create a *reminder* (e.g., "Time for the weekly track. Reply [Explicit Approval] to start."). When the user replies in the chat, launch the subagents via `Agent` so they render visibly in the UI.
- **Scopus MCP (resolved 2026-08-21):** `scopus-mcp` is registered in Claude Code at `C:\Users\User\.claude.json` under `mcpServers.scopus`. Two things were required to make it work and must not be reverted: the real `SCOPUS_API_KEY` (the placeholder `PUT_YOUR_KEY_HERE` was the original failure), and the args `["--with", "mcp<2.0.0", "scopus-mcp"]` — the package declares an unpinned `mcp>=0.1.0`, so `uvx` pulls `mcp 2.0.0`, whose `Server` class dropped `list_tools()` and crashes the server on import. MCP changes only take effect after a **full desktop-app restart**.
- **Local File Reading vs UI Uploads ("Invalid API Key" Error):** If the user attempts to upload a `.docx` draft or PDF via the Desktop UI paperclip/drag-and-drop and encounters an "Invalid API key" error, it means the UI is trying to send the file directly to the LLM provider (e.g. Gemini/OpenAI) which lacks the proper file endpoint permissions. **Do not ask them to fix their API key.** Instead, instruct the user to provide the absolute file path (e.g. `D:\<PROJECT>\document.docx`) so you can use the built-in `Read` tool to parse the document locally without hitting external APIs.
- **Canonical location & synchronization:** The **live** copy of this skill — the one Claude Code actually loads — is `C:/Users/User/.claude/skills/hermes-research/skills/deep-science-writer/`. Edit that one. Two other copies exist and are **not** loaded: `C:/Users/User/.claude/skills/learned/research-writing/deep-science-writer/` (the original Hermes-era version, kept for Hermes and as the source of the bundled `.venv`/`node_modules`, which the live copy reaches via directory junctions) and `C:/Users/User/workspace/deep-research-agent/skills/deep-science-writer/` (the GitHub mirror). After changing the live copy, mirror it to the workspace repo, commit with a conventional commit message, and push to `origin/main`; the live copy is the source of truth on conflict.

## Lessons from the 2026-08 Fukuoka run (field-tested, not theoretical)

A full four-subagent literature sweep was executed end to end in August 2026. These are the failures that actually occurred and the fixes that actually worked.

### Elsevier full text: use the Scopus key, not a browser

**The registered `SCOPUS_API_KEY` also authorises Elsevier's Article Retrieval API.** This retrieves full text for every Elsevier journal — Remote Sensing of Environment, Urban Climate, Urban Forestry & Urban Greening, Applied Geography, Cities, Solar Energy — as clean text, with no browser, no proxy, and no PDF extraction step.

```python
import requests, json
KEY = json.load(open(r"C:/Users/User/.claude.json", encoding="utf-8"))["mcpServers"]["scopus"]["env"]["SCOPUS_API_KEY"]
r = requests.get(f"https://api.elsevier.com/content/article/doi/{doi}?httpAccept=text/plain",
                 headers={"X-ELS-APIKey": KEY, "Accept": "text/plain"}, timeout=60)
```

`pii/{PII}` also works (take the PII from Crossref's `alternative-id`); `httpAccept=text/xml` preserves section structure. Sleep ~1 s between calls. Six paywalled papers were retrieved this way in one pass after every crawler route had failed. **Try this before reaching for cloakbrowser on any `10.1016/` DOI.**

Publisher routing that works:

| Publisher | Route |
|---|---|
| Elsevier (`10.1016/`) | Article Retrieval API with the Scopus key, as above |
| MDPI (`10.3390/`) | `www.mdpi.com/.../pdf` returns Access Denied, but the asset CDN `https://res.mdpi.com/<journal>/<journal>-<vol>-<page>/article_deploy/<...>.pdf` serves it |
| Copernicus (BG, ACP, ESSD) | Fully open: `https://bg.copernicus.org/articles/<vol>/<page>/<year>/bg-<vol>-<page>-<year>.pdf` |
| Nature / Sci Rep | `https://www.nature.com/articles/<id>.pdf` when OA |
| PMC | Public PMC sits behind reCAPTCHA; the Europe PMC mirror `https://europepmc.org/articles/PMC<id>?pdf=render` does not |
| Wiley / AGU | No reliable automated route found; needs institutional access |

Note that OpenAlex `oa_status` is not a reliable predictor here — papers reading `closed` in OpenAlex retrieved fine through the Elsevier API.

### Verify downloaded content, not just the file format

A guessed NTRS identifier returned a perfectly valid 1.2 MB PDF that was a NASA launch-abort-system paper, not the requested Landsat calibration study. Checking for a `%PDF` magic number and a plausible size is **not** sufficient. Read page 1 and match expected title keywords before trusting any download:

```python
d = fitz.open(path)
first = d[0].get_text("text").lower()
assert "expected keyword" in first and "second keyword" in first
```

### Never propagate a subagent's number without checking the primary source

Subagent reports are leads, not evidence. Two concrete errors from this run:

- A Scopus subagent reported that a manuscript value "sits almost exactly on the national mean". The source paper stated plainly *"biomass and ANPP are all dry-matter based"* and defined ANPP as aboveground only. The comparison needed a dry-matter-to-carbon conversion (x0.45-0.50) **and** a belowground addition (+20-40%). Both were missing; the conclusion inverted once corrected.
- A subagent could not attribute two numbers to the right study site from the indexed abstract and correctly said so. Once the full text was retrieved, the direction of the finding was the opposite of what the abstract fragment implied.

**Rule:** before a subagent-reported number enters a synthesis or a manuscript, grep it out of the primary full text and read the sentence around it. Reserve this for load-bearing numbers; you cannot re-verify everything, so say plainly which numbers were re-verified and which were taken on report.

### Background scripts must checkpoint per query, never write at the end

Two of four subagents initially reported "nothing usable" and both were wrong:

- One launched its sweep as `python ... | tail -70`, so all stdout buffered inside `tail` and nothing appeared until exit; the script also wrote its JSON only after all 53 queries finished, so an interrupted run yielded nothing. It had in fact completed, with 9,088 records.
- One hit anonymous-pool 429s on Semantic Scholar and stopped before its citation-graph track.

**Fix in the script, not in the retry:** redirect to a log file instead of piping to `tail`, and checkpoint the results JSON after every query so a killed run still yields partial data. Cache responses so a re-run resumes rather than repeats.

### Citation-graph traversal finds what keyword search cannot

Semantic Scholar's `/paper/DOI:{doi}/citations` revealed the structural reason a literature gap existed: the 53 papers citing the main site-context paper contained **zero** carbon or NPP work — the urban-greenspace literature and the carbon-cycle literature were disconnected communities. Keyword search on the site name could never have surfaced the numbers, because they live in a citation neighbourhood that never touches it. A single bridging paper connected the two.

**Use citation-graph traversal when keyword search returns thematically narrow results.** It is a ~20-call job with a key. Note that `SEMANTIC_SCHOLAR_API_KEY` is currently unset, and the backup file stores only a masked placeholder (`s2k-V9...Zw6N`, literal ellipsis) — the anonymous pool 429s heavily and a real key turns a 25-minute grind into about a minute.

### Reading PDFs

Prefer the `markitdown` skill over raw PyMuPDF text extraction: it renders tables as Markdown pipe tables, which matters for papers whose load-bearing numbers live in a regional or parameter table. Fall back to PyMuPDF only when markitdown errors on a specific file.
