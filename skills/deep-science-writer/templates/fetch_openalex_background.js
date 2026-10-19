// OpenAlex harvest with cross-search tracking (references/research-workflows.md §0).
// Copy into the run folder, edit QUERIES, run in the background:
//   node fetch_openalex_background.js > harvest.log 2>&1
// Checkpoints after every query and caches each response, so a killed run keeps its
// data and a re-run resumes. Nothing is sampled: every non-MDPI record is written.

const fs = require('fs');
const path = require('path');
const https = require('https');
const crypto = require('crypto');

// One entry per search. `filter` is appended to BASE_FILTER, e.g.
//   'publication_year:<2016'                era-gated, older vocabulary
//   'publication_year:>2020'                era-gated, recent
//   'type:article|review'                   SR/MA searches: many meta-analyses are indexed as article
const QUERIES = [
    { subarea: 'mechanism', q: 'your 4-8 word query', filter: '' },
    { subarea: 'mechanism', q: 'systematic review OR meta-analysis your topic', filter: 'type:article|review' },
];
const BASE_FILTER = 'has_abstract:true';
const PER_PAGE = 50;                        // OpenAlex allows up to 200
const MAILTO = process.env.OPENALEX_MAILTO || '';   // polite pool; set before use
// Repeat-hit threshold: 3 sub-areas for 10+ searches, 2 for 5-search budgets.
const FOUNDATIONAL_MIN = QUERIES.length >= 10 ? 3 : 2;
const GROUP_MIN = 3;                        // same author in this many records -> research group
// Full-text trigger (SKILL.md Phase 1 step 8): every concept the question hinges on, one regex
// each, e.g. ['spline', 'CASA|GLO-?PEM']. A record counts only if its title + abstract match ALL.
// Fewer than KEY_TERMS_MIN such records -> run scripts/fulltext_search.py.
// In a JS string a word boundary is '\\b'; a single '\b' is a backspace and silently never matches.
const KEY_TERMS = [];
const KEY_TERMS_MIN = 5;
KEY_TERMS.forEach(t => { if (/[\x00-\x1f]/.test(t)) throw new Error(`KEY_TERMS entry ${JSON.stringify(t)} holds a control character: write '\\\\b', not '\\b'`); });

const OUT = 'openalex_harvest';
const CACHE = path.join(OUT, 'cache');
fs.mkdirSync(CACHE, { recursive: true });

function get(url) {
    return new Promise((resolve) => {
        https.get(url, { headers: { 'User-Agent': `deep-science-writer/2.0${MAILTO ? ` (mailto:${MAILTO})` : ''}` } }, (res) => {
            let data = '';
            res.on('data', c => data += c);
            res.on('end', () => resolve({ status: res.statusCode, body: data }));
        }).on('error', e => resolve({ status: 0, body: String(e) }));
    });
}

async function search(entry) {
    const filter = [BASE_FILTER, entry.filter].filter(Boolean).join(',');
    const url = `https://api.openalex.org/works?search=${encodeURIComponent(entry.q)}`
        + `&filter=${encodeURIComponent(filter)}&per-page=${PER_PAGE}${MAILTO ? `&mailto=${MAILTO}` : ''}`;
    const key = path.join(CACHE, crypto.createHash('sha1').update(url).digest('hex') + '.json');
    if (fs.existsSync(key)) return { ...JSON.parse(fs.readFileSync(key, 'utf8')), cached: true };
    const r = await get(url);
    let out;
    try {
        const j = JSON.parse(r.body);
        out = r.status === 200
            ? { status: 200, available: j.meta?.count ?? null, results: j.results || [] }
            : { status: r.status, error: j.error || j.message || r.body.slice(0, 200), results: [] };
    } catch (e) {
        out = { status: r.status, error: 'unparseable response: ' + r.body.slice(0, 200), results: [] };
    }
    if (out.status === 200) fs.writeFileSync(key, JSON.stringify(out));   // never cache failures
    return out;
}

const normDoi = d => (d || '').toLowerCase().replace(/^https?:\/\/(dx\.)?doi\.org\//, '');
const isMdpi = w => (w.primary_location?.source?.host_organization_name || '').toLowerCase().includes('mdpi')
    || normDoi(w.doi).startsWith('10.3390');
function decodeAbstract(inv) {
    if (!inv) return '';
    const words = [];
    for (const [w, pos] of Object.entries(inv)) for (const p of pos) words[p] = w;
    return words.filter(Boolean).join(' ');
}

function checkpoint(records, log) {
    const year = new Date().getFullYear();
    const recs = Object.values(records).map(r => ({
        ...r,
        sub_area_hits: [...new Set(r.hits.map(h => h.subarea))],
        cites_per_year: +(r.cited_by_count / Math.max(1, year - (r.year || year) + 1)).toFixed(1),
    }));
    recs.forEach(r => { r.foundational = r.sub_area_hits.length >= FOUNDATIONAL_MIN; });
    const keyRes = KEY_TERMS.map(t => new RegExp(t, 'i'));
    recs.forEach(r => { r.all_key_terms = keyRes.length > 0 && keyRes.every(re => re.test(`${r.title || ''} ${r.abstract}`)); });
    const keyHits = recs.filter(r => r.all_key_terms).length;
    const keyLine = keyRes.length === 0
        ? 'Full-text trigger: KEY_TERMS not set, so the abstract count was not measured.'
        : `Full-text trigger: ${keyHits} of ${recs.length} abstracts match all KEY_TERMS [${KEY_TERMS.join(' ; ')}] -> `
          + (keyHits < KEY_TERMS_MIN ? `fewer than ${KEY_TERMS_MIN}: RUN full-text search.` : `${KEY_TERMS_MIN} or more: abstracts suffice on this measure.`);
    const authors = {};
    recs.forEach(r => r.authors.forEach(a => { authors[a] = (authors[a] || 0) + 1; }));
    const groups = Object.entries(authors).filter(([, n]) => n >= GROUP_MIN).sort((a, b) => b[1] - a[1]);
    fs.writeFileSync(path.join(OUT, 'records.json'), JSON.stringify(recs, null, 1));
    fs.writeFileSync(path.join(OUT, 'search_log.json'), JSON.stringify(log, null, 1));

    const cell = s => String(s ?? '').replace(/\|/g, '/').replace(/\s+/g, ' ');   // `type:article|review` would split a column
    const rows = log.map(l => `| ${cell(l.subarea)} | ${cell(l.q)} | ${cell(l.filter)} | ${l.status}${l.cached ? ' (cache)' : ''} | ${l.returned} | ${l.available ?? ''} | ${l.mdpi_excluded} | ${cell(l.error)} |`);
    const top = [...recs].sort((a, b) => b.sub_area_hits.length - a.sub_area_hits.length || b.cites_per_year - a.cites_per_year);
    const md = [
        '# OpenAlex harvest summary', '',
        `Unique records: ${recs.length}. Foundational (hit in >= ${FOUNDATIONAL_MIN} sub-areas): ${recs.filter(r => r.foundational).length}.`, '',
        keyLine, '',
        '| Sub-area | Query | Filter | HTTP | Returned | Available | MDPI excluded | Error |', '|---|---|---|---|---|---|---|---|', ...rows, '',
        `## Research groups (>= ${GROUP_MIN} records)`, '', ...groups.map(([a, n]) => `- ${a}: ${n}`), '',
        '## Records by sub-area hits, then citations per year', '',
        '| Hits | Sub-areas | Cites/yr | Year | First author | Title | DOI |', '|---|---|---|---|---|---|---|',
        ...top.map(r => `| ${r.sub_area_hits.length} | ${cell(r.sub_area_hits.join(', '))} | ${r.cites_per_year} | ${r.year} | ${cell(r.authors[0])} | ${cell(r.title)} | ${r.doi || r.id} |`),
    ].join('\n');
    fs.writeFileSync(path.join(OUT, 'summary.md'), md);
}

async function main() {
    const records = {};
    const log = [];
    for (const entry of QUERIES) {
        const r = await search(entry);
        let mdpi = 0;
        for (const w of r.results) {
            if (isMdpi(w)) { mdpi++; continue; }
            const key = normDoi(w.doi) || w.id;
            records[key] ??= {
                doi: normDoi(w.doi), id: w.id, title: w.title, year: w.publication_year, type: w.type,
                cited_by_count: w.cited_by_count || 0,
                journal: w.primary_location?.source?.display_name || '',
                authors: (w.authorships || []).map(a => a.author?.display_name).filter(Boolean),
                abstract: decodeAbstract(w.abstract_inverted_index), hits: [],
            };
            records[key].hits.push({ subarea: entry.subarea, q: entry.q });
        }
        log.push({ ...entry, status: r.status, cached: !!r.cached, available: r.available, returned: r.results.length, mdpi_excluded: mdpi, error: r.error });
        console.log(`[${r.status}] ${entry.subarea} | ${entry.q} -> ${r.results.length}${r.error ? ' ERROR ' + r.error : ''}`);
        checkpoint(records, log);
        if (!r.cached) await new Promise(res => setTimeout(res, 1000));
    }
    const failed = log.filter(l => l.status !== 200).length;
    console.log(`Done: ${Object.keys(records).length} unique records, ${failed} failed searches. See ${OUT}/summary.md`);
    if (failed) process.exitCode = 2;      // a failed search is not an empty literature
}

main();
