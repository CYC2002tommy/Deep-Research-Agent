# Search strategies: sub-area, facets, syllabus

Adapted on 2026-10-19 from the three workflows Consensus publishes at
`consensus.app/home/mcp` (literature review helper, grant research, curriculum
development). **Only the method was taken. The Consensus MCP is not used**; the
user declined it. Every "search" below goes to the sources this skill already
has: Scopus, Exa, OpenAlex, Semantic Scholar, AnySearch.

The strategy, stop gate, budget tier and source floor are chosen in the Phase 0
blueprint (SKILL.md Phase 0 step 4). Read §0 first; each strategy adds its own steps.

---

## 0. Shared rules (every strategy)

1. **Provenance.** Cite only records that a search in this session returned. Anything
   from memory or outside knowledge is labelled `[not from search]` and does not count
   toward a reading list, a gap, or an evidence table.
2. **Sparse is not a gap.** If a sub-area comes back thin, say how thin and why it might
   be thin: the page cap, a 429, an exhausted quota, an over-narrow query. The Fukuoka
   run had two subagents report "nothing usable" and both were wrong. Call something a
   literature gap only after at least two sources and one reworded query agree.
3. **Atomic queries.** 4-8 words, shaped "core topic + applied angle" (for a water-supply
   course: "membrane fouling drinking water treatment", not "membrane fouling"). One concept
   pair per query; see "Intersection of Zero" in SKILL.md.
4. **Track across searches, not within one.** One table keyed by DOI (lower-case, no
   `https://doi.org/` prefix): sub-areas it was hit in, first author, year, citations,
   citations per year = `cited_by_count / (current_year - year + 1)`.
   `templates/fetch_openalex_background.js` builds this table; merge Scopus, Exa and
   AnySearch hits into it by DOI.
   - Hit in several sub-areas -> likely foundational. Threshold: 3 sub-areas when the run
     has 10+ searches, 2 when it has 5 (with only 4-5 orthogonal queries, 3 is usually empty).
   - The same author in 3+ records -> a research group.
   - Highest citations per year -> the seminal paper, not just the most-cited one.
5. **Search summary at the end of every search phase.** Queries run per source, records
   returned and available, unique after DOI dedupe, MDPI excluded, selected, and the thin
   sub-areas with the reason from rule 2.
6. **Evidence level.** Abstracts are enough for screening, overview tables and reading-list
   summaries; label those abstract-level. Mechanisms, load-bearing numbers, gap quotes and
   prose claims need the full text (SKILL.md, full-text rule).

### Filter mapping (Consensus filter -> our sources)

| Intent | OpenAlex (live-tested 2026-10-19) | Scopus (live-tested 2026-10-19) | Semantic Scholar `/paper/search` |
|---|---|---|---|
| Year floor/ceiling | `publication_year:>2020` / `publication_year:<2016` | `PUBYEAR > 2020` | `year=2021-` / `year=-2015` |
| Reviews, SR, MA | "systematic review" / "meta-analysis" in the query **and** `type:article\|review` (many meta-analyses are indexed as `article`; `type:review` alone drops them) | `DOCTYPE(re)` plus the same query terms without the doctype limit | `publicationTypes=Review,MetaAnalysis` |
| Citation floor | `cited_by_count:>20` | `sort=-citedby-count`, filter locally | `minCitationCount=20` |
| Open access | `is_oa:true` | `OPENACCESS(1)` | `openAccessPdf` (presence) |
| Journal quality | none in the API: apply the Q1/Q2 + no-MDPI rule downstream | same | same |

OpenAlex filters combine with commas: `filter=type:article|review,publication_year:>2020`.
OpenAlex `search=` matches loosely (44,975 "available" for a four-word query in testing),
so screen titles. The Semantic Scholar parameters are from its API documentation; the
anonymous pool returned 429 on 2026-10-19, so they were not live-tested that day.

---

## 1. `sub-area` — map a field

Use when the user wants to know what a literature says, who the groups are, and where
the gaps are. At the `map` gate the deliverable is the map (Markdown + vault note); at
`section` or `manuscript` it becomes the Phase 1 table and feeds the Phase 0.5 Gap Report.

**1. RECON** is SKILL.md Phase 0 step 3. Its vocabulary and high-citation papers shape
the plan.

**2. PLAN** (part of the Phase 0 blueprint).
- Framework:
  - **PICO** (Population, Intervention, Comparison, Outcome): health, behavioural,
    education, social questions.
  - **SPIDER** (Sample, Phenomenon of Interest, Design, Evaluation, Research type):
    qualitative or lived-experience questions with no intervention.
  - **Decomposition** (Mechanism, Applications, Limitations, Comparisons): technology,
    engineering and Earth-system topics. Usually the right one for this user's work.
- 4-5 sub-areas, each with a one-line rationale.
- Budget:

| Tier | Searches | Allocation |
|---|---|---|
| quick | 5 | one per sub-area |
| standard | 10 | 5 sub-area + 2 systematic-review/meta-analysis on the two broadest sub-areas + 2 era-gated on the most important sub-area (one `<2016`, one `>2020`) + 1 AnySearch `academic.citation` (`op=references` and `op=citations`) on the top 1-2 seed DOIs |
| exhaustive | SKILL.md Phase 1, all five sources | |

A search is one query run on every source the blueprint names. The era-gated pair is there
to catch terminology shifts (e.g. "gut flora" -> "gut microbiome"); record any shift found.
The citation-graph slot replaces Consensus's keyword follow-up: it reaches work that shares
no vocabulary with the query (Fukuoka lesson in SKILL.md).

**3. SEARCH.** Sequentially, within each source's rate limit, tracking as in §0 rule 4.

**4. SYNTHESIZE.** Sections, in order:
1. **Topic overview**: one paragraph. What it is, the framework used, where the evidence
   is dense and where it is sparse.
2. **Start here**: 5-7 papers in reading order for a newcomer: the best recent review, the
   foundational paper(s), 2-3 frontier papers, one paper on a live controversy or gap. Per
   paper: what it contributes, and what to watch for while reading.
3. **How the field got here**: a short narrative plus a 5-8 row table
   `| Year | Milestone | Significance |`, with terminology shifts noted.
4. **Sub-area guides**: per sub-area, what the research shows (2-3 sentences, cited), 3-5 key
   papers (citations, year, why it matters), and the queries actually run for it.
5. **Key research groups**: 3-5 recurring authors with affiliation, sub-areas and one
   representative paper.
6. **Open questions and gaps**, three kinds, each with one "why it matters" line:
   methodological (weak designs, small samples, inconsistent measures);
   population / context (regions, climates, scales, systems not studied);
   conceptual (contradictions not reconciled, mechanisms not tested, adjacent fields not
   connected). Back each with a gap quote where one exists (§2 step 3).
7. **Bibliography**: APA 7th, alphabetical, full DOI.
8. **Search summary** (§0 rule 5).

---

## 2. `facets` — gap quotes and a positioning narrative

Use for a manuscript Introduction, a proposal's significance and innovation section
(NSTC 研究背景與目的, a friend's 研究計畫), or a reply that needs "nobody has done X". The
question is not "is this novel?" but "what text can the author defend?". The narrative is
prose the user will paste into a document, so the stop gate is `section` or higher.

**1. Five facet searches**, restricted to roughly the last six years:

| # | Facet | Query intent |
|---|---|---|
| 1 | Established | what the field agrees on about the core concept |
| 2 | Stakes | burden, magnitude, exposure, cost or emissions in the target system or region |
| 3 | Current approaches and limits | methods, models, guidelines in use today |
| 4 | Method in adjacent contexts | the proposed method applied elsewhere: feasibility evidence, or whitespace |
| 5 | The gap | reviews and perspectives on the field's open problems ("<field> challenges future directions", with `type:article\|review`); Exa full-text search for the gap phrases below |

**2. Dedupe by DOI.** Papers hit by several facets are high-signal.

**3. Extract 3-5 verbatim gap quotes** from the full texts of the 5-10 high-signal papers,
in their Discussion, Limitations and Conclusions sections, where authors state limitations
in their own words. In the CPP-comammox run the gap was established this way: the stated
weakness of Blom et al. (2025), Cu(I) activity loss, and the absence of "peptide" were both
checked in the full text. Phrases to grep for: "future research should", "remains unclear", "remains poorly
understood", "no studies have", "has not been examined", "limited evidence", "little is
known", "critical gap", "further work is needed", "to our knowledge". Each quote carries
author, year and DOI and is copied exactly from the downloaded text, never retyped. A quote
that cannot be found in a downloaded text is not used.

**4. Positioning narrative**, three paragraphs the author can adapt:
- P1: what the field has established (facet 1), and why it matters here (facet 2).
- P2: what current approaches do (facet 3), and where they fall short, carried by two of the
  gap quotes.
- P3: what this project proposes; the adjacent-context evidence (facet 4) that it is
  feasible; and that the gap shows it has not been done in this system, region or scale.

Strict literalism from SKILL.md applies twice over: a gap quote about one region, biome or
scale supports a gap in that region, biome or scale only.

**Who funds similar work** (proposals only, on request). The source workflow tallies NIH
RePORTER by institute, study section and funding notice. For this user's NSTC proposals
the equivalent is a manual search of the Government Research Bulletin (`grb.gov.tw`). For
a US call, look up the funder's awards API at the time. One trap already found: the
RePORTER template Consensus publishes fails as written; the API wants `abstracttext`, not
`abstract`, in `search_field`, and `FullStudySection`, not `StudySection`. Funded projects
are context for differentiation, never evidence for a scientific claim.

---

## 3. `syllabus` — a course reading list

Use for TA work and course preparation. Usually stops at the `map` gate.

1. **Parse.** Extract the ordered topics and the course learning outcomes. If no outcomes
   are stated, infer 3-5 and label them inferred. Group topics into 6-12 sections. The
   grouping goes into the Phase 0 blueprint for approval.
2. **Search.** 1-2 queries per section, 4-8 words, "core topic + applied angle" with the
   course's applied domain in every query. Default to the last two years; widen a section
   only when it is thin, and say so.
3. **Select** 1-3 papers per section, 15-25 in total, in this priority: relevance; reviews and
   meta-analyses over narrow primary studies (a better entry point for students); citations;
   fit to the applied domain. The Q1/Q2 + no-MDPI rule still holds.
4. **Write**, per paper, from what the retrieved record actually says (abstract-level, §0
   rule 6):
   - **Summary**: one plain-language sentence a second-year student would want to read,
     jargon defined in parentheses.
   - **Discussion question**: one question tied to a named learning outcome that asks the
     student to apply, analyse or evaluate. Never a recall question ("what did the authors
     find?").
   If the record is too thin to summarise, say so instead of guessing.
5. **Output**: course header (title, date range); 2-3 sentences on how the list was built and
   how to use it; the learning outcomes; the sections, each with numbered entries (title with
   DOI link, authors, journal, year, Summary, Discussion question); the search summary, naming
   thin sections ("Nitrogen removal returned one paper; supplement by hand").
