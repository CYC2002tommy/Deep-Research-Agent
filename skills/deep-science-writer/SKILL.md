---
name: deep-science-writer
description: "End-to-end scientific research pipeline combining Exa Search, Playwright, deep-research, text-humanization, and iterative Remi peer review."
---

# Deep Science Writer (End-to-End Pipeline)

This skill orchestrates a multi-stage pipeline for scientific research, combining neural search, browser automation, academic synthesis, and humanized writing. It merges the capabilities of Exa Search, Playwright, Google Science Skills, Deep Research, and Text Humanization into one cohesive workflow.

## 🎯 Trigger Conditions
- User asks to write a scientific article, literature review, or deep-dive research report.
- User requests comprehensive research using web searching and scraping (Exa + Playwright).
- The output requires rigorous academic citations (APA 7th) but a highly natural, human-like reading flow.

## 📋 Workflow Steps

### Phase 0: Mandatory Deep Context Gathering & Research Plan
1. Incorporate academic rigor from `nature-skills`, structured literature parsing from `academic-research-skills`, and cross-validation techniques from `superpowers`. Keep their principles active in context.
2. **Mandatory Interrogation:** You MUST deeply understand the user's current research topic before doing anything else. If the user's initial prompt is too brief, you MUST actively interrogate them to extract their exact pain points, research hypotheses, and core objectives. Do NOT proceed until you fully grasp the context.
3. **Mandatory Pre-Flight Discussion:** Once the context is understood, formulate a preliminary research plan (proposed keywords, target databases, expected article structure, and goals).
4. Present this blueprint to the user to discuss the research direction. Focus on delegating the heavy lifting to parallel subagents via `delegate_task` to protect the main context window.
5. **Halt & Wait:** You MUST wait for the user's "Explicit Approval" of the research plan before proceeding to Phase 0.5.

### Phase 0.5: Background Sourcing, Full-Text Deep Reading, & Gap Analysis
1. **Large-Scale Abstract Screening:** Delegate subagents or write a background script to fetch a large pool of abstracts (e.g., 100+ papers) via APIs. Screen these abstracts for strict relevance and Q1/Q2 quality first.
2. **Targeted Full-Text Downloading:** Once the abstracts are verified to match the research need, the script MUST download or scrape the *entire full text* of the filtered subset (e.g., top 20-30 papers).
3. **Deep Reading & Filtering:** Read the downloaded full texts (specifically Methodology and Results) to extract the actual mechanisms. Discard any papers that fail to substantiate the claims in their abstracts or overstate findings.
4. **Long-Running Execution:** Execute the script using `terminal(background=true, notify_on_complete=true)`. Wait for the background notification before proceeding.
5. **Mandatory Justification & Gap Report:** Before moving to synthesis or drafting, you MUST present a structured evaluation report to the user containing exactly these three sections:
   - **Selection Rationale (為什麼讀這幾篇)**: Explicitly explain how these specific papers map precisely to the user's stated topic and pain points.
   - **Research Gap (研究缺口在哪)**: Identify what these papers leave unsolved or unaddressed, defining the exact gap in the current literature.
   - **Topic Enhancement (對課題有什麼提升)**: Clearly articulate how these findings can be fed back into the user's project to improve their experimental design, strengthen their argument, or correct their research trajectory.
6. **Synthesis & Synthesis Mastery:** Only after the user approves the Gap Report, spawn **Subagent C** (Master Synthesizer) to merge and critically analyze the findings into a formal academic synthesis report. *(Note: Override the user's general chat preference for concise lists; use standard formal academic prose here.)*

### Phase 1: Strict Multi-Agent Discovery (`scopus-mcp` + `exa-search` + `openalex` + `semantic-scholar`)
1. **Journal Quality Filter**: ONLY include Q1 and Q2 papers. If a Q3 paper provides crucial evidence, you MUST explicitly mark it in the text/table with `[Q3]`. STRICTLY EXCLUDE any Q4 papers and ANY papers published by MDPI.
2. **Mandatory 3-Subagent Deployment**: You MUST spawn exactly three subagents using `delegate_task` to handle different geographical or thematic queries concurrently.
3. **Mandatory Subagent Rules**: The subagents MUST strictly adhere to the MDPI/Q4 exclusion rules. 
4. **Mandatory Toolset Utilization**: Each subagent (or the collective effort) MUST explicitly utilize ALL of the following databases to ensure exhaustive coverage:
   - `scopus-mcp` (for Elsevier/authoritative DB)
   - `exa-search` (for neural web search and Open Access discovery)
   - OpenAlex API (via Python/Node.js scripts, strictly filtering out MDPI)
   - Semantic Scholar API (via Python/Node.js scripts)
   Failure to use all four sources is a violation of this skill.
5. **Exhaustive Mapping (User Rule)**: Do NOT sample (e.g., just looking at 5 out of 20). Process the *exhaustive* set of relevant findings into a structured Markdown table: `| Title | Authors/Year | Key Finding | URL/DOI |`.

### Phase 2: Deep Extraction (`cloakbrowser` + `deep-research`)
1. **Dynamic Scraping**: For high-value sources that require JavaScript rendering, interaction, or are heavily dynamically loaded, use the **CloakBrowser** tool/CLI to navigate, bypass anti-bot protections, wait for specific DOM selectors, and extract the full text. Do NOT use standard Playwright for this, as CloakBrowser is the primary scraper.
2. **Synthesis**: Cross-reference extracted findings across multiple sources to validate claims and identify consensus vs. controversy. 

### Phase 3: Structural Drafting (`article-writing`)
1. Outline the article based on `article-writing` principles: strong hook, logical progression, evidence-backed claims, and clear logical headings.
2. Integrate data explicitly. Use block equations or Mermaid diagrams if explaining complex systems or workflows.
3. Format all inline citations and the final reference list strictly in **APA 7th** format. When generating via `python-docx`, programmatically implement APA hanging indents (`p.paragraph_format.first_line_indent = Inches(-0.5)` and `p.paragraph_format.left_indent = Inches(0.5)`) and ensure journal/book titles and volume numbers are properly italicized.

### Phase 4: Humanization & Polish (`text-humanizer`)
1. Review the generated draft and ruthlessly strip AI-isms, applying the strict **"No Fluff"** style profile.
2. **Banned AI Vocabulary**: "delve", "tapestry", "in conclusion", "crucial", "testament", "realm", "fosters", "underscores", "moreover".
3. **Style Adjustments**: 
   - Use varied sentence lengths (short, punchy sentences mixed with complex ones).
   - Prefer active voice over passive voice.
   - Remove introductory meta-commentary ("Here is the article...").
   - Ensure the prose flows like a subject-matter expert speaking directly to a peer.

### Phase 4.5: Anti-Hallucination & Evidence Verification
**Strict Requirement:** This phase MUST be completed before Remi (Phase 5) is allowed to review the manuscript.
1. **Extraction**: Scan the draft and extract every single in-text citation (e.g., Smith, 2024) and its corresponding Reference List entry.
2. **DOI/URL Liveness Test**: Use the `terminal` tool (via `curl -I`), Exa Search MCP, or a Python script (e.g., `requests.get` / `urllib`) to ping every DOI or URL in the reference list. For bulk or programmatic URL resolution when links are missing, execute `scripts/verify_urls.py` (uses `ddgs` and `requests`).
   - **STRICT REPLACEMENT RULE**: If a DOI/URL is dead (404) or fake, you MUST NOT simply delete the sentence or claim. You MUST trigger a targeted secondary search (Exa/Scopus) to find a real Q1/Q2 replacement paper that supports the exact claim. Download the new full-text, verify it, and insert the new citation.
3. **Claim Grounding Check**: Cross-reference the specific claims made in the draft against the raw data/abstracts collected in Phases 1 & 2. 
   - **Strict Literalism (就事論事)**: Never over-extend findings. If a claim overstates the actual findings, down-modulate it. 
   - **No Concept Stitching**: Do not stitch a macro/global finding (e.g., "planetary boundaries") with a localized context (e.g., "European summer extremes") in the same citation unless the source explicitly connects them. Stick strictly to the literal facts. If a study analyzes a broad region (e.g., "global temperate drylands"), do not misattribute its specific localized mechanism to a single city (e.g., "Paris") just because that city sits within the region.
- **Differentiate Plant Functional Types (PFTs)**: When interpreting drought resilience, strictly differentiate between shallow-rooted ground vegetation (grass) and deep-rooted urban trees. Do not mistakenly apply a "plant shutdown" mechanism to trees if the literature explicitly states only the ground vegetation was affected due to shallow soil moisture depletion.
4. **Continuous Replacement Loop**: Repeat the search, replacement, and verification process until **EVERY single factual statement or claim in the manuscript is backed by a verified, live reference**.
5. **Pass Condition**: Zero dead links, zero fake DOIs, zero ungrounded claims, and 100% of claims supported by valid references. Only then proceed to Phase 5.

### Phase 4.6: Zotero Archiving & PDF Download
**Strict Requirement:** This phase bridges verified evidence with bibliography management before Remi's review.
1. **PDF Retrieval**: For every paper successfully verified in Phase 4.5, utilize `scripts/fetch_oa_fulltexts.py` or `CloakBrowser` to download the Full-Text PDF to the local `assets/` directory.
   - Prioritize Open Access links via Unpaywall. If Paywalled, attempt browser-based fetching via University IP.
2. **Zotero Ingestion (via `pyzotero`)**: 
   - Load the `pyzotero` skill to integrate with the Zotero v3 API.
   - For each verified paper, create a Parent Item in Zotero (e.g., `journalArticle`) populated with title, authors, year, DOI, and URL.
3. **PDF Attachment**:
   - Use `zot.attachment_simple([local_pdf_path], parentid=parent_key)` to upload the downloaded PDF as an attachment to its respective Zotero Parent Item.
4. **Error Handling**: If a PDF cannot be downloaded due to aggressive Paywalls, log the failure but still create the Parent Item in Zotero with the DOI/URL to ensure the bibliography record exists.

### Phase 5: Peer Review & Iteration (`remi`)
1. Load the `remi` skill (`skill_view(name='remi')`) to act as a strict Nature/Science-level peer reviewer.
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
2. **Document Compilation (`docx` or `python-docx`)**: You MUST NOT just output Markdown as the final product. Write a Python script using `python-docx` to programmatically build the final Word document. *Important Windows Environment Note*: When executing the Python script via `terminal`, use absolute paths with forward slashes and enclose them in quotes (e.g., `python "C:/path/to/generate_docx.py"`) to prevent MSYS bash from stripping backslashes and causing `[Errno 2] No such file or directory`.
3. **Embed Assets**: Insert the generated AntV Infographic images and any Mermaid charts into the `.docx` file at the appropriate logical sections. Ensure formatting aligns with APA 7th standards (e.g., proper figure captions).
4. **Final Delivery**: Save the generated `.docx` file directly to the `D:\` drive (e.g., `D:\Research_Report.docx`). Deliver this absolute D:\ path to the user.

### Phase 7: Knowledge Base & NotebookLM Integration
1. **Obsidian Wiki Update**: Synthesize the core findings, literature insights, and strategic takeaways. Write or append this synthesis directly into the user's Obsidian Vault (`C:\Users\User\Documents\Obsidian Vault\Hermes\`) to maintain an ongoing, centralized knowledge base.
2. **NotebookLM Source Ingestion**: Utilize the `notebooklm` MCP tools to create a dedicated notebook for this research project. You MUST explicitly upload **every single cited reference** as an **individual source** into NotebookLM (do not just upload one compiled document). Upload the raw abstracts or full-texts for each cited paper so NotebookLM can accurately cross-reference and map individual citations.

## 📚 Linked References
- `references/python-docx-manipulation.md`: Patterns for reading, creating, and safely removing XML paragraphs from `.docx` files.
- `references/academic-api-patterns.md`: Reliable curl and Python patterns for hitting Crossref and OpenAlex APIs, including critical URL-encoding fixes.
- `scripts/verify_urls.py`: Python script utilizing `ddgs` and `requests` to programmatically search and verify evidence URLs for Phase 4.5.
- `scripts/node/fetch_openalex_papers.js`: Node.js script for safely fetching from OpenAlex and strictly filtering out MDPI/Q4.
- `scripts/node/fetch_unpaywall_oa.js`: Resolves DOI to Open Access PDF URLs via Unpaywall.
- `scripts/node/scrape_html_fulltext.js`: Scrapes HTML full texts to bypass basic PDF blocks.
- `scripts/node/extract_pdf_text.js`: PDF parsing script template using `pdf-parse`.
- `scripts/node/generate_docx.js`: Programmatically generates APA 7th compliant DOCX using the `docx` library.
- `templates/fetch_openalex_background.js`: Node.js template for background fetching from the OpenAlex API, including the logic to decode `abstract_inverted_index` and respect rate limits.
- `scripts/fetch_oa_fulltexts.py`: Python script utilizing the Unpaywall API and PyMuPDF to automatically locate, download, and extract text from Open Access PDFs for a given list of DOIs. Crucial for Phase 0.5.
- `templates/fetch_openalex_background.js`: Node.js template for background fetching from the OpenAlex API, including the logic to decode `abstract_inverted_index` and respect rate limits.

## ⚠️ Pitfalls & Strict Rules

- **Zotero Credentials & Setup:** Phase 4.6 relies on the `pyzotero` client. The pipeline will crash or fail to archive if the required environment variables (`ZOTERO_API_KEY`, `ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE`) are missing. Always verify these are present in the environment or a `.env` file before executing the pipeline.
- **STRICT COMPLIANCE REQUIRED:** You MUST strictly follow EVERY step of this pipeline in order. Skipping phases, ignoring instructions, or taking shortcuts (such as writing drafts without full-text verification) is strictly forbidden. There are no exceptions.
- **English Output ONLY:** All generated drafts, reports, and final documents MUST be written strictly in English, regardless of the conversational language.
- **FULL-TEXT READING IS MANDATORY (NO ABSTRACT-ONLY SHORTCUTS):** You MUST NOT rely solely on abstracts. You MUST download, scrape, or extract the *entire full text* of the papers before synthesizing or extracting mechanisms. If full text is inaccessible, you MUST drop the paper or ask the user for help. DO NOT proceed to drafting based only on OpenAlex/Scopus abstracts.
- **No Hallucinated Citations:** Every claim MUST map to a real URL/DOI found during Phase 1/2.
- **Strict Literalism vs. Concept Stitching (Scale & Region Mismatch):** NEVER map physiological/mechanistic findings from one geographical study to an unrelated region, OR from a macro-biome scale to a specific city. If a study covers "Global Temperate Drylands", do NOT explicitly attribute its findings to the urban environment of "Paris" (Geographical Over-Extrapolation). If you lack city-specific data, explicitly run an additional targeted search instead of concept-stitching macro data to fit the prompt. Read and report the literal findings.
- **Cherry-Picking and Data Reversal (PFT Conflation):** Do not ignore the primary conclusion of a paper to isolate a minor variable that fits a preconceived narrative. Pay extreme attention to contrasting functional types within a paper: if a study finds that shallow-rooted *grasses* suffer severe drought stress while deep-rooted *trees* remain resilient, do not conflate the two and falsely claim the trees are suffering (Plant Functional Type Conflation). Read the nuances of the data.
- **MDPI Exclusion & 403 Errors:** MDPI servers (DOI prefix `10.3390`) aggressively block headless requests (curl/node), resulting in 403 Forbidden errors during Phase 4.5 URL verification. Do NOT just fetch them and fail later. When writing the Phase 0.5 background fetch script (e.g., using OpenAlex), **programmatically filter out MDPI** by checking `host_organization_name` (must not include "mdpi") and `doi` (must not include "10.3390") *before* processing or presenting the results to the user.
- **Paywalled Literature (Elsevier/Scopus):** Standard APIs (Crossref/Exa) cannot fetch full text from closed databases. Use `scripts/fetch_oa_fulltexts.py` to check Unpaywall first. If still paywalled, spawn a subagent using **CloakBrowser** to navigate to the article URL directly—if the host machine is on a university network, this automatically leverages IP-based access while bypassing bot protections.
- **Action Over Planning:** Do not tell the user what you *will* do. Immediately start executing Exa Search and Playwright tool calls.
- **Table First:** Always build and present the literature/evidence table *before* writing the final prose.
- **Intersection of Zero (Query Formulation):** When cross-analyzing highly specific variables (e.g., comparing 4 distinct cities simultaneously), NEVER combine them into a single academic API search query (e.g., Crossref/Semantic Scholar). This yields zero results. Deconstruct the research into atomic, independent searches (e.g., "Paris drought NPP", "Singapore UHI NPP") and synthesize the results post-retrieval.
- **API Rate Limits & Terminal Environments:** Semantic Scholar public APIs aggressively rate-limit (HTTP 429). Implement delays (`time.sleep`) and use minimal batch sizes when scraping. If 429 errors persist, pivot immediately to OpenAlex or Crossref APIs. For Scopus API, complex nested boolean logic with `NOT` may throw `400 Bad Request`; fetch broader results and filter locally via Python. On Windows hosts, the `terminal` tool runs MSYS bash. Always use `python -m pip install` and execute absolute paths using forward slashes and quotes (e.g., `python "C:/path/to/script.py"`) to prevent backslashes from being stripped by the shell. Additionally, when passing absolute Windows paths to python commands, MSYS bash may strip the backslashes causing `[Errno 2] No such file or directory`. Always use forward slashes for paths in terminal execution.
- **OpenAlex Strict Filtering:** When querying the OpenAlex API via custom scripts, you MUST programmatically exclude MDPI and low-tier publishers by strictly checking the `host_organization_name` field (e.g., rejecting "Multidisciplinary Digital Publishing Institute" or "MDPI").
- **Windows MSYS Execution Context:** On Windows hosts, the `terminal` tool runs MSYS bash where standard `python` and `pip` commands may fail or open the Windows Store. Always use `py script.py` to run scripts and `py -m pip install` to install dependencies. For background async tasks and PDF extraction, Node.js (`node`) is heavily preferred as it natively handles async loops well in the MSYS terminal without alias issues. See `references/nodejs-pdf-extraction.md` for stable `pdf-parse` templates.
- **Visible Background Agents (Desktop UI vs Cronjobs):** If the user asks to "see" subagents working in the Desktop UI (e.g. for scheduled tracking), do NOT use a standard silent background `cronjob`. Cronjobs run headless and are invisible in the UI. Instead, update the `cronjob` to act as a *reminder* (e.g., "Time for the weekly track. Reply [Explicit Approval] to start."). When the user replies in the chat, launch the subagents via `delegate_task` so they are rendered visibly in the UI (limited by `max_concurrent_children`, usually 3).
- **Missing MCP Servers after Environment Migration:** If the user moves their `.hermes` folder to a new drive/machine, external MCP servers (like `scopus-mcp`) defined in the old `config.yaml` are not automatically transferred to the new active config. If the tool is unexpectedly missing, manually check the old `config.yaml` and append the configuration to the current `~/AppData/Local/hermes/config.yaml`.
- **Missing MCP Servers after Environment Migration:** If the user moves their `.hermes` folder to a new drive/machine, external MCP servers (like `scopus-mcp`) defined in the old `config.yaml` are not automatically transferred to the new active config. If the tool is unexpectedly missing, manually check the old `config.yaml` and append the configuration to the current `~/AppData/Local/hermes/config.yaml`.
- **Local File Reading vs UI Uploads ("Invalid API Key" Error):** If the user attempts to upload a `.docx` draft or PDF via the Desktop UI paperclip/drag-and-drop and encounters an "Invalid API key" error, it means the UI is trying to send the file directly to the LLM provider (e.g. Gemini/OpenAI) which lacks the proper file endpoint permissions. **Do not ask them to fix their API key.** Instead, instruct the user to provide the absolute file path (e.g. `D:\Tommy\document.docx`) so you can use the built-in `read_file` tool to parse the document locally without hitting external APIs.
- **Skill Synchronization (GitHub Repository):** The source code for this skill is mirrored in `C:/Users/User/workspace/deep-research-agent/skills/deep-science-writer/`. Whenever you modify the `SKILL.md` or scripts in the local `AppData` directory, you MUST actively copy those changes to the workspace repository, commit with a standard conventional commit message, and push to `origin/main`. If a git pull conflict occurs, overwrite the workspace version with the updated `AppData` version as the source of truth.
