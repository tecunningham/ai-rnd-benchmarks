# AI R&D benchmarks in closed-lab model cards: collection and verification notes

Two passes on 2026-09-13. Pass 1 (web search only; every lab site blocked) produced the first
table from snippets and memory. Pass 2 (network opened) read every card PDF or page directly and
rewrote `data/ai_rd_benchmarks.csv`: 396 rows, of which 371 are `reported` (read from the card or
the METR report it cites), 10 `announcement` (launch post; the card has no such number), 12
`snippet` and 3 `memory` (launch-blog figures found in no primary document). Part A below is the
verification record per lab; Part B is the original collection notes, kept for the query log.

# Part A: verification against the cards (pass 2)

# GDM model-card verification notes (2026-09-13)

Input: `gdm_current.csv` (30 rows, all `snippet`/`memory`). Output: `gdm_verified.csv` (53 rows: 29 existing rows kept/corrected, 1 existing row dropped-and-replaced in place, 24 new rows). Working files (PDFs, extracted text, table images) are in `gdm_cards/`.

## Documents read

| Document | URL | What was read |
|---|---|---|
| Gemini 2.0 Flash Model Card (published Apr 15, 2025), 7 pp. | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-2-0-Flash-Model-Card.pdf | Whole card (text). The old URL modelcards.withgoogle.com/assets/documents/gemini-2-flash.pdf now returns the deepmind.google model-card index HTML. |
| Gemini 2.5 Pro Model Card (last updated Jun 27, 2025), 21 pp. | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-2-5-Pro-Model-Card.pdf | Benchmark table (pp. 5-6), Frontier Safety section incl. Table 1, ML R&D section, Figure 4 image (p. 18). |
| Gemini 2.5 technical report (arXiv 2507.06261), 73 pp. | https://arxiv.org/pdf/2507.06261 | Table 3/4 (SWE-bench), Sec. 5 Frontier Safety, Machine Learning R&D subsection (pp. 33-34, Figure 12). |
| Gemini 2.5 Deep Think Model Card (published Aug 1, 2025), 20 pp. | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-2-5-Deep-Think-Model-Card.pdf | Frontier Safety section (CCL table, ML R&D, Figure 4 image p. 16, correctness checks). No SWE-bench/Terminal-Bench in this card. |
| Gemini 3 Pro Model Card (Model Release Nov 2025, Last Updated May 2026), 10 pp. | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf (deepmind.google/models/model-cards/gemini-3-pro/ redirects here) | Whole card; benchmark table is an image (p. 5), read visually. |
| Gemini 3 Pro Frontier Safety Framework Report (Nov 2025), 26 pp. | https://storage.googleapis.com/deepmind-media/gemini/gemini_3_pro_fsf_report.pdf | pp. 1-6 (summary table), pp. 13-16 (ML R&D CCL definitions, RE-Bench methodology, Figure 4 image), misalignment section. |
| Gemini 3 Flash Model Card (Dec 2025), 6 pp. | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Flash-Model-Card.pdf | Whole card; table image (p. 4). |
| Gemini 3.1 Pro Model Card (Feb 2026), 9 pp. + HTML page | PDF https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-1-Pro-Model-Card.pdf ; HTML https://deepmind.google/models/model-cards/gemini-3-1-pro/ | Whole card; table image (p. 4) and HTML table; FSF results table (pp. 8-9). |
| Gemini 3.5 Flash Model Card (May 2026), 7 pp. + HTML | PDF .../Gemini-3-5-Flash-Model-Card.pdf ; HTML https://deepmind.google/models/model-cards/gemini-3-5-flash/ | Whole card; table image (p. 4) and HTML table (they differ, see below). |
| Gemini 3.6 Flash Model Card (Jul 2026), 7 pp. + HTML | PDF .../Gemini-3-6-Flash-Model-Card.pdf ; HTML .../gemini-3-6-flash/ | Whole card; table image (p. 4) and HTML table. |
| Gemini 3.7 Flash Model Card (Aug 2026), 9 pp. + HTML | PDF .../Gemini-3-7-Flash-Model-Card.pdf ; HTML .../gemini-3-7-flash/ | Whole card; table image (p. 5) and HTML table; FSF summary table (p. 9). |
| Gemini 3.7 Flash Frontier Safety Framework Report (Aug 2026), 41 pp. | https://storage.googleapis.com/deepmind-media/gemini/gemini_3-7_flash_fsf_report.pdf | pp. 1-4 (overview), pp. 34-41 (ML R&D and Misalignment: CCL/TCL definitions, GRB benchmark, results, elicitation, SSA evals). |
| Gemini 3.8 Flash Model Card (Sep 2026), 8 pp. + HTML | PDF .../Gemini-3-8-Flash-Model-Card.pdf ; HTML .../gemini-3-8-flash/ | Whole card; table image (p. 5) and HTML table. |

Probed and not found (404): deepmind.google/models/model-cards/gemini-3-deep-think/, .../Gemini-3-Deep-Think-Model-Card.pdf, .../gemini-2-5-deep-think/ (HTML), .../Gemini-2-5-Pro-Preview-Model-Card.pdf. There is no standalone Gemini 3 Deep Think card.

## Key findings

1. **The 1.04 RE-Bench figure for Gemini 3 Pro is not in the Gemini 3 Pro card or FSF report.** The FSF report gives methodology and a bar chart (Figure 4, per-task, no numeric labels) but no aggregate number. The 1.04 appears only in the Gemini 3.1 Pro card as the comparator. Row kept at 1.04 with source = 3.1 Pro card.
2. **Gemini 3 Pro FSF RE-Bench protocol (verbatim, p. 14):** 32-hour cumulative budget; 16 attempts per challenge with a 2-hour limit each; bootstrap samples of 16 runs drawn from 24; max within each sample (mean for Scaling Law Experiment); 5 of 7 tasks (Finetune GPT-2 for QA and Scaffolding for Rust Codecontest omitted, need internet); METR modular scaffold with minimal changes. The existing note's "human baseline 71 eight-hour attempts by 61 experts" is not in the report (human results are "sourced from the original work").
3. **Gemini 2.5 Pro card Table 1 gives a numeric RE-Bench average: 0.73** ("average normalised score is 0.73") for Gemini 2.5 Pro Experimental (03-25), recalculated with METR's methodology in the May 2025 correction. The GA column gives only the 50-125% best-run range. New row added. Tech report protocol: two settings, 43 x 45-min runs and 16 x 2-hour runs (64 and 24 actual runs).
4. **Gemini 3.7 Flash FSF report does NOT give a RE-Bench score.** ML R&D CCLs are assessed with a single internal benchmark, **GRB** (74 research-engineering tasks, 2-hour timeout, internal scaffold): Gemini 3.7 Flash **pass@1 27%** (rule-out threshold 90%; ~20% of tasks bugged, conservative max 47%); Gemini 3.1 Pro roughly 16% (preliminary). The Stealth and Situational Awareness TCL (new in FSF v3.1, April 2026) not reached: 3/4 stealth, 6/11 situational awareness. Rows added for both models (family `ml_rd_internal`), plus an explicit "not reported" RE-Bench row for 3.7 Flash.
5. **Terminal-Bench numbers from third-party blogs were wrong:** 3.7 Flash is 85.8% (not 81.6%), 3.8 Flash is 89.4% (not 90.8%), both Terminal-bench 2.1. Cards from 3.7 Flash also report Terminal-bench 3.0 (14.9%) and, for 3.8 Flash, Terminal-bench 4.0 (19.1%); rows added.
6. **Gemini 3.5 Flash card has no SWE-bench Verified row** (only Terminal-bench 2.1 and SWE-Bench Pro (Public)). The 78.8% row stays `snippet` with a note. Cards from 3.5 Flash onward report SWE-Bench Pro (Public) and, from 3.6 Flash, DeepSWE v1.1; the 3.6 Flash card is the only one that reports **MLE-Bench** (3.6 Flash 63.9%, 3.5 Flash 49.7%, 3.1 Pro 42.6%).
7. **HTML vs PDF discrepancy, Gemini 3.5 Flash card:** PDF snapshot shows SWE-Bench Pro 53.9% (3 Flash 48.4%); the live HTML page shows 55.1% (3 Flash 49.6%), matching the 3.6 Flash card comparator. Recorded 55.1% / 49.6% with a note.
8. **Cross-card comparator drift:** 3 Pro Terminal-Bench 2.0 is 54.2% in its own card and the 3 Flash card, 56.9% in the 3.1 Pro card. 3.1 Pro Terminal-bench 2.1 is 70.3% in the 3.5 Flash card and 73.8% in the 3.6 Flash card. 3.6 Flash DeepSWE is 49% in its own card, 48.6% in the 3.7 Flash card. Noted in the rows.
9. **Gemini 2.0 Flash card contains no FSF results.** It only lists "Frontier Safety Framework evaluations" as an evaluation type; no domains, results or CCL determination. The old row's "evaluated, no CCL reached" was not supported; corrected to "not reported". SWE-bench Verified for 2.0 Flash (21.4% single / 34.2% multiple) added from the 2.5 tech report Table 3.
10. **Gemini 3 Pro card was revised (Last Updated May 2026)** and now covers Deep Think mode: "Frontier Safety evaluations of Gemini 3 Pro using Deep Think mode yielded results consistent with the original Gemini 3 Pro assessment." The Deep Think row's card_date changed from 2025-12 to 2026-05 (insertion date of that sentence cannot be verified).

## Row-by-row changes

### Existing rows (30)
- 2.0 Flash / ML R&D determination: **corrected** (score_text "evaluated, no CCL reached" -> "not reported"; card_url fixed to deepmind-media PDF). reported.
- 2.5 Pro / RE-Bench best run 50-125%: **confirmed**; conditions expanded (GA; 43x45min or 16x2h; 5 of 7 tasks); source -> card PDF. reported.
- 2.5 Pro / ML R&D determination: **confirmed**; verbatim CCL definitions added. reported.
- 2.5 Pro / SWE-bench Verified 67.2% multiple attempts: **confirmed** (GA). reported.
- 2.5 Pro / SWE-bench Verified 59.6% single attempt: **confirmed**; memory note corrected (63.8% is the Experimental 03-25 single-attempt figure in the June card, 63.2% for Preview 05-06). reported.
- 2.5 Deep Think / ML R&D determination: **confirmed** (was memory); "The overall performance falls short of our alert threshold." reported.
- 3 Pro / RE-Bench 1.04: **kept**, conditions corrected (5 of 7 tasks; 2-hour limit per attempt), note corrected (1.04 only in 3.1 Pro card; human-baseline claim removed). reported (source = 3.1 Pro card).
- 3 Pro / ML R&D determination: **confirmed**; CCL definitions added from FSF p. 13. reported.
- 3 Pro / SWE-bench Verified 76.2%: **confirmed**. reported.
- 3 Pro / Terminal-Bench 2.0 54.2%: **confirmed** (Terminus-2 agent); 56.9% in 3.1 Pro card noted. reported.
- 3 Deep Think / determination: **confirmed**; card_date -> 2026-05; title adjusted. reported.
- 3 Flash / determination: **confirmed** (was memory). reported.
- 3 Flash / SWE-bench Verified 78.0%: **confirmed**; source -> card. reported.
- 3 Flash / Terminal-Bench 2.0 47.6%: **confirmed** (was memory). reported.
- 3.1 Pro / RE-Bench 1.27: **confirmed**; conditions note that protocol is not restated in card. reported.
- 3.1 Pro / Optimize LLM Foundry 47 s: **confirmed**. reported.
- 3.1 Pro / determination: **confirmed**. reported.
- 3.1 Pro / SWE-bench Verified 80.6%: **confirmed** (single attempt, Thinking High). reported.
- 3.1 Pro / Terminal-Bench 2.0 68.5%: **confirmed** (Terminus-2 harness). reported.
- 3.5 Flash / determination: **confirmed**. reported.
- 3.5 Flash / SWE-bench Verified 78.8%: **not in card**; left as snippet with note. UNVERIFIED.
- 3.5 Flash / Terminal-Bench 2.1 76.2%: **confirmed**; source -> card. reported.
- 3.6 Flash / determination: **confirmed**; note corrected (card does not cite the April 2026 FSF). reported.
- 3.6 Flash / Terminal-Bench 2.1 78.0%: **confirmed**; source -> card. reported.
- 3.6 Flash / SWE-Bench Pro 58.7%: **confirmed**. reported.
- 3.7 Flash / determination: **confirmed and refined** (alert threshold not reached; TCL not reached; no RE-Bench). reported.
- 3.7 Flash / Terminal-Bench 2.1: **corrected** 81.6% -> 85.8%. reported.
- 3.7 Flash / DeepSWE v1.1 65.3%: **confirmed**; source -> card. reported.
- 3.8 Flash / determination: **confirmed**. reported.
- 3.8 Flash / Terminal-Bench 2.1: **corrected** 90.8% -> 89.4%. reported.

### New rows (24)
2.0 Flash SWE-bench Verified 21.4% (tech report); 2.5 Pro RE-Bench average 0.73 (Exp 03-25); 2.5 Pro SWE-bench Verified 63.8% (Exp 03-25); 2.5 Deep Think RE-Bench (figure only, protocol); 3 Pro SWE-Bench Pro 43.3%; 3 Flash Terminal-Bench 2.1 58.0% and SWE-Bench Pro 49.6%; 3.1 Pro Terminal-Bench 2.1 73.8%, SWE-Bench Pro 54.2%, DeepSWE 12%, MLE-Bench 42.6%, GRB ~16%; 3.5 Flash SWE-Bench Pro 55.1%, DeepSWE 37%, MLE-Bench 49.7%; 3.6 Flash DeepSWE 49%, MLE-Bench 63.9%; 3.7 Flash RE-Bench not reported, GRB 27%, Terminal-Bench 3.0 14.9%, FrontierCode 1.1 43.6%; 3.8 Flash Terminal-Bench 4.0 19.1%, DeepSWE 73.7%.

## Still unverified / caveats
- Gemini 3.5 Flash SWE-bench Verified 78.8%: not in any GDM card; third-party only.
- Gemini 3 Pro RE-Bench 1.04: primary GDM source is the 3.1 Pro card, not a 3 Pro document. Per-task RE-Bench scores for 2.5 Pro, 2.5 Deep Think and 3 Pro exist only as unlabeled bar charts (Figure 4 in each), so no per-task numbers were added beyond the 3.1 Pro Optimize LLM Foundry runtime.
- 3.7 Flash and 3.8 Flash cards do not state the Terminal-bench harness (earlier cards say Terminus-2).
- MLE-Bench metric/subset (medal rate vs other) is not specified in the 3.6 Flash card; metric recorded as "% (medal rate as reported)" - treat the label as an assumption.
- Comparator numbers reprinted in later cards (e.g. 3 Pro Terminal-Bench 56.9% in the 3.1 Pro card) sometimes differ from the model's own card; rows use the model's own card where it exists and note the discrepancy.
- Card dates are month-level "Published" fields from the cards; the 3 Pro card is a May 2026 revision of a Nov 2025 card.

---

# OpenAI system-card verification notes (2026-09-13)

Task: verify `openai_current.csv` (AI self-improvement / model-autonomy benchmark rows from OpenAI system cards) against the primary cards; output `openai_verified.csv` (same header).

## Summary counts
83 input rows -> 144 output rows. Of the 83 rows that map to input rows: 70 confirmed from a primary card (confidence=reported), 25 of those carry a 'Corrected 2026-09-13' note (value/attribution/condition/URL changed), 11 remain unverified (snippet/memory), 1 marked not_in_card, 1 metr_report. 61 rows added.

Confidence vocabulary used in `openai_verified.csv`:
- `reported` - value/wording confirmed in the primary system card named in `source_url` (text or chart label; where a value was read from an unlabelled curve the notes say "approx. read from chart" and `score` is left blank).
- `snippet` / `memory` - carried over unchanged; the figure is NOT in any system card (launch-blog / aggregator figures) and could not be verified because openai.com blog pages were unreachable (curl 403 and egress-blocked).
- `not_in_card` - the card was checked and contains no such evaluation (GPT-5.2 SWE-Lancer).
- `metr_report` - value verified against METR's own statement, not present in the card (GPT-5.2 6.6 h).

## Documents read (primary)
All PDFs downloaded to `openai_cards/` and text-extracted with pypdf; figure pages rendered with PyMuPDF and read visually (chart labels).
- GPT-4o System Card, Aug 8 2024 - https://cdn.openai.com/gpt-4o-system-card.pdf (pp.13-18: 3.8 Model autonomy, 4.1 METR)
- OpenAI o1 System Card, Sep 12 2024 (o1-preview/o1-mini) - https://cdn.openai.com/o1-system-card.pdf (pp.12-13 METR; pp.28-32 4.5 Model Autonomy)
- OpenAI o1 System Card, Dec 5 2024 - https://cdn.openai.com/o1-system-card-20241205.pdf (pp.14-15 METR; pp.34-41 5.8 Model Autonomy)
- OpenAI o3-mini System Card, Jan 31 2025 (feb10 revision) - https://cdn.openai.com/o3-mini-system-card-feb10.pdf (pp.25-31 5.7)
- Deep Research System Card, Feb 25 2025 (SWE-Lancer note Jul 28 2025) - https://cdn.openai.com/deep-research-system-card.pdf (pp.27-34 3.4.7)
- OpenAI GPT-4.5 System Card, Feb 27 2025 - https://cdn.openai.com/gpt-4-5-system-card-2272025.pdf (p.6-7 METR; pp.18-25 4.6). Card URL corrected from the openai.com index page (which returns 403 to curl) to this PDF.
- OpenAI o3 and o4-mini System Card, Apr 16 2025 - https://cdn.openai.com/pdf/2221c875-02dc-4789-800b-e7758f3722c1/o3-and-o4-mini-system-card.pdf (pp.9-10 METR; p.11 Preparedness; pp.22-28 4.4)
- Addendum to o3 and o4-mini system card: Codex, May 16 2025 - https://cdn.openai.com/pdf/8df7697b-c1b2-4222-be00-1fd3298f351d/codex_system_card.pdf (p.8 2.5 Preparedness; whole document read)
- ChatGPT Agent System Card, Jul 17 2025 - https://cdn.openai.com/pdf/6bcccca6-3b64-43cb-a66e-4647073142d7/chatgpt_agent_system_card_launch.pdf (pp.27-32 5.1.3)
- GPT-5 System Card, Aug 13 2025 - https://cdn.openai.com/gpt-5-system-card.pdf (pp.35-43 5.1.3 incl. 5.1.3.7 METR)
- Addendum to GPT-5 system card: GPT-5-Codex, Sep 15 2025 - https://cdn.openai.com/pdf/97cc5669-7a25-4e63-b15f-5fd5bdc4d149/gpt-5-codex-system-card.pdf (whole document; p.5 Preparedness)
- GPT-5.1 Instant and GPT-5.1 Thinking System Card Addendum, Nov 12 2025 - https://cdn.openai.com/pdf/4173ec8d-1229-47db-96de-06d87147e07e/5_1_system_card.pdf (whole document; p.4 Preparedness Framework)
- GPT-5.1-Codex-Max System Card, Nov 18 2025 - https://cdn.openai.com/pdf/2a7d98b1-57e5-4147-8d0e-683894d782ae/5p1_codex_max_card_03.pdf (pp.19-26 5.1.3)
- Update to GPT-5 System Card: GPT-5.2, Dec 11 2025 - https://cdn.openai.com/pdf/3a4153c8-c748-4b71-8e31-aecbde944f8d/oai_5_2_system-card.pdf (p.16 Preparedness; pp.20-26 4.1.3)
- Addendum to GPT-5.2 System Card: GPT-5.2-Codex, Dec 18 2025 - https://cdn.openai.com/pdf/ac7c37ae-7f4c-4442-b741-2eabdeaf77e0/oai_5_2_Codex.pdf (pp.16-22 5.1.3)
- GPT-5.3-Codex System Card, Feb 5 2026 - https://cdn.openai.com/pdf/23eca107-a9b1-4d2c-b156-7deb4fbc697c/GPT-5-3-Codex-System-Card-02.pdf (pp.18-21 5.1.3) + https://deploymentsafety.openai.com/gpt-5-3-codex/ai-self-improvement
- GPT-5.4 Thinking System Card, Mar 5 2026 - https://deploymentsafety.openai.com/gpt-5-4-thinking/gpt-5-4-thinking.pdf (p.16; pp.25-29 5.1.3; p.36 Table 20) + .../gpt-5-4-thinking/ai-self-improvement
- GPT-5.5 System Card, Apr 23 2026 - https://deploymentsafety.openai.com/gpt-5-5/gpt-5-5.pdf (p.21; pp.35-39 9.1.3) + .../gpt-5-5/ai-self-improvement
- OpenAI GPT-5.6 System Card, dated 2026-07-09 (changelog Aug 3 and Aug 19 2026) - https://deploymentsafety.openai.com/gpt-5-6/gpt-5-6.pdf (pp.1-2 intro; p.35 designations; pp.56-68 9.1.3 incl. 9.1.3.6 METR) + .../gpt-5-6/ai-self-improvement-capabilities. No separate "June preview" card was found; card_title updated accordingly.
- GPT-6 Astra System Card, published Sep 3 2026, revised Sep 9 2026 - https://deploymentsafety.openai.com/gpt-6-astra (web only; sections 1, Preparedness overview, 10.1.3 AI Self-Improvement Capabilities; chart PNGs image52-56/43 fetched from .../data/eval-sets/gpt-6-astra/assets/images/). No PDF located; no METR section found.

Secondary/external checked: METR GPT-5 report (metr.org/evaluations/gpt-5-report/), METR GPT-5.1-Codex-Max report (metr.org/evaluations/gpt-5-1-codex-max-report/), METR GPT-5.6 Sol summary (metr.org/blog/2026-06-26-gpt-5-6-sol/), METR X post on GPT-5.2 (6.6 h). openai.com launch blogs returned 403 / were egress-blocked, so launch-only figures stay unverified.

## Rows changed and why (prefix "Corrected 2026-09-13" in `notes`)
- GPT-4o | Agentic tasks (autonomy suite) | 0% - was qualitative only
- o1 | SWE-bench Verified | 48% - conditions were 'internal tools scaffold'
- o1 | OpenAI Research Engineer interviews | 78% (pre and post); GPT-4o 60% - absolute value filled from card chart (GPT-4o 60%, o1-mini 74%/77%, o1-preview 80%/83%, o1 78%/78%)
- o1 | OpenAI Research Engineer interviews | 83%; GPT-4o 73% - absolute value filled from the o3-mini / GPT-4
- o3-mini | OpenAI Research Engineer interviews | 92% - was '93%, pass@128 (metric from memory)'
- deep research | SWE-bench Verified | 68% (with and without browsing) - confidence was 'memory' (recalled from GPT-4
- GPT-4.5 | AI self-improvement (earlier: model autonomy) classification | Model autonomy: Low - card_url was the openai
- GPT-4.5 | SWE-bench Verified | 38% (post-mitigation); 35% (pre) - conditions were 'internal tools scaffold' (not stated in card)
- o3 / o4-mini | SWE-bench Verified | o3 68% (no browsing) / 69% (browsing); o4-mini 69% / 68%; o3 helpful-only 71% - was 'o3 69
- o3 / o4-mini | PaperBench | o3 18%; o4-mini 24% (chart label 25%) - was 'about 22 to 24%'
- ChatGPT agent | PaperBench | 22% - was 'highest scoring model to date, with browsing'
- GPT-5 | SWE-bench Verified | 74% (card); 74.9% (launch blog, medium verbosity) - score was 74
- GPT-5 | SWE-Lancer IC SWE Diamond | 55% (ChatGPT agent 60%) - was 'no improvement over prior models' with no number
- GPT-5.1 | SWE-Lancer IC SWE Diamond | 62% - was 67%
- GPT-5.1 | OpenAI-Proof Q&A | 0% - was 2%
- GPT-5.2 | MLE-bench | 16% (GPT-5.2 card); 12.2% (as re-run in GPT-5.4 card) - was 12
- GPT-5.2 | SWE-Lancer IC SWE Diamond | not in card - was 'reported on 197 of 237 tasks; 40 tasks that did not run omitted'
- GPT-5.3-Codex | AI self-improvement (earlier: model autonomy) classification | AI self-improvement: below High - removed unverified note that early versions were used to debug the model's own training (not found in the card text)
- GPT-5.4 Thinking | OpenAI-Proof Q&A | 4.16% - was 5
- GPT-5.4 Thinking | Internal Research Debugging Eval | 49.4% - value filled
- GPT-5.4 Thinking | Monorepo-Bench | 59.33% - value filled
- GPT-5.5 | Monorepo-Bench | 60% - was 'little improvement' with no number
- GPT-5.6 Sol | AI self-improvement (earlier: model autonomy) classification | AI self-improvement: below High (High in bio/chem and cyber; below Critical in cyber) - quote tidied
- GPT-5.6 Sol | MLE-bench | 87.18% (max; from GPT-6 Astra card); 5.6 card gives cost/latency curves only - was '48
- GPT-6 Astra | AI self-improvement (earlier: model autonomy) classification | AI self-improvement: below High (first model at Critical in cybersecurity; High in bio/chem) - was 'designation not confirmed'

Other notable confirmations/attribution fixes without a value change:
- o1 MLE-bench 24% pass@10 derivation confirmed by the Dec 2024 chart (o1 post 14%/24%, pre 15%/27%, o1-preview 16%/37%, GPT-4o 8%/18%).
- GPT-5.1 OpenAI PRs 45% confirmed as gpt-5.1 (Codex-Max card chart: gpt-5 45%, gpt-5.1 45%, codex-max 53%).
- GPT-5.2 MLE-bench: the 12.2% is indeed gpt-5.2-thinking, but as re-run in the GPT-5.4 card; the GPT-5.2 card's own figure is 16%.
- o3 PaperBench: o3 launch candidate 18%, o4-mini 24% (text; chart label 25%), o1 24% (o3/o4-mini card); the GPT-5 card later shows o3 at 21% on the 10-paper subset.
- ChatGPT agent MLE-bench 9% and SWE-Lancer 60% come from the GPT-5 card (the agent card has neither); source_url set to the GPT-5 card.
- o1 SWE-bench 48% is an Agentless re-run in the o3-mini card, not an internal-tools result.
- METR GPT-5: card says ~2h15m (65m-4h30m); METR report says 2h17m (65m-4h25m). Codex-Max: card 2h42m (75m-350m); METR ~2h40m (75m-5h50m). GPT-5.6 Sol: METR 11.3 h (5-40 h) with cheating scored as failure, not considered robust.

## Rows added (61)
Per-benchmark values for every model from the card's self-improvement/model-autonomy section that were missing: GPT-4o (SWE-bench 19%, RE interviews), o1-preview (RE MCQ, agentic 42%, METR Sep 2024), o1 (PRs 12%, SWE-Lancer, PaperBench 24%), o3-mini (MLE-bench 11%/20%, SWE-Lancer 14%, PaperBench 8%), deep research (RE, agentic 80%, MLE 11%, PRs 42%, SWE-Lancer 53%), GPT-4.5 (RE, agentic 40%, MLE 11%, PRs 7%, SWE-Lancer 20%/$41,625, METR ~30 min), o3/o4-mini (RE, PRs 44%/39%, SWE-Lancer 54%/$86,100), ChatGPT agent (SWE-bench 62%, PRs 42%, RE MCQ 75%, SWE-Lancer 60%, OPQA 1%), GPT-5 (PRs 45%), GPT-5-Codex (designation, SWE-Lancer 67%), GPT-5.1 (designation), GPT-5.2 (PRs 55%, PaperBench 39%, OPQA 3%, Monorepo 56.70%), GPT-5.2-Codex (designation, PRs 55%, MLE 10%, PaperBench 43%, OPQA 8%, Monorepo 54.67%), GPT-5.3-Codex (Monorepo 56%, OPQA 6%, IRDE 44.1%), GPT-5.6 Sol (IRDE, KernelGen 1P, NanoGPT, PostTrainBench Lite - curves only), GPT-6 Astra (IRDE 78.05%, KernelGen, NanoGPT, PostTrainBench Lite - curves, MLE-Bench Revised 93.80%).

## Still unverified (11 rows, all launch-blog/aggregator figures that do not appear in any system card)
- codex-1 | SWE-bench Verified | 72.1% pass@1; 83.8% pass@8 | snippet
- GPT-5-Codex | SWE-bench Verified | 74.5% | snippet
- GPT-5.1-Codex-Max | SWE-bench Verified | 77.9% | snippet
- GPT-5.1-Codex-Max | Terminal-Bench | 58.1% | snippet
- GPT-5.2 | SWE-bench Verified | 80.0% | memory
- GPT-5.2-Codex | SWE-Bench Pro | 56.4% | snippet
- GPT-5.3-Codex | SWE-Lancer IC SWE Diamond | 81.4% | snippet
- GPT-5.3-Codex | SWE-Bench Pro | 56.8% | snippet
- GPT-5.3-Codex | Terminal-Bench | 77.3% | snippet
- GPT-5.5 | SWE-Bench Pro | 58.6% | snippet
- GPT-5.5 | Terminal-Bench | 82.7% | snippet

Also: GPT-5.2 SWE-Lancer row is `not_in_card` (origin of the "197 of 237 tasks" note not found); GPT-5.2 METR 6.6 h is `metr_report` (METR statement, no metr.org report page located). GPT-5.6 / GPT-6 Astra KernelGen, NanoGPT, PostTrainBench Lite and 5.6 IRDE values are curve readings only (score blank).

## Caveats
- Chart labels were read from rendered PDF pages; values marked "approx. read from chart" are eyeballed from unlabelled curves and should not be quoted as exact.
- Several cards report multiple variants (pre/post-mitigation, browsing/no browsing, helpful-only/launch candidate); `score` uses the launch-candidate, post-mitigation, no-browsing figure unless noted in `score_text`.

---

# Anthropic AI R&D benchmark verification — notes (2026-09-13)

Input: `anthropic_current.csv` (105 rows, all `snippet`/`memory`).
Output: `anthropic_verified.csv` (200 rows, same header, written with Python `csv`).

Confidence vocabulary used in the output:

| value | meaning |
|---|---|
| `reported` | confirmed against the primary system card PDF (or, where stated in `notes`, against a later Anthropic system card that prints the value) |
| `announcement` | not in any card; confirmed against Anthropic's own launch post (`anthropic.com/news/...`) |
| `metr_report` | not in any card; confirmed against METR's published evaluation report |
| `snippet` / `memory` | unchanged from input — could not be confirmed in any primary Anthropic or METR document |

Result: 184 `reported`, 10 `announcement`, 3 `metr_report`, 1 `snippet`, 2 `memory`.
Of the 105 input rows, 20 carry a `Corrected 2026-09-13: was ...` (or `Restructured`) note; 94 rows were added.

Working files (PDFs, extracted text, section dumps, build script) are in `anthropic_cards/` and `build_verified.py` in the scratchpad.

## 1. Documents read

Every card was downloaded, text-extracted with pypdf, flattened to one line per page, and the RSP/AI R&D and capability sections read in full. Where the anthropic.com landing page resolved to a newer CDN hash than the URL in the input, the newer copy was downloaded and text-diffed against the older one; in every case the AI R&D numbers were unchanged (differences were changelogs, page shifts, and unrelated corrections).

| Model | Card (canonical URL, date on title page) | Pages read for this task | Notes on URL/date |
|---|---|---|---|
| Claude 3.5 Sonnet | https://www-cdn.anthropic.com/fed9cc193a14b84131812372d8d5857f8f304c52/Model_Card_Claude_3_Addendum.pdf (PDF created 2024-06-20) | all 8 | unchanged |
| Claude 3.5 Sonnet (Oct 2024) | https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf (PDF created 2024-10-22) | all 14 | unchanged |
| Claude 3.7 Sonnet | https://www-cdn.anthropic.com/9ff93dfa8f445c932415d335c88852ef47f1201e/claude-3-7-sonnet-system-card.pdf (no date printed; Feb 2025) | 24, 28–33 (7.2 Autonomy) | landing page resolves to this hash; text identical to the `assets.anthropic.com/m/785e23...` copy in the input |
| Claude Opus 4 / Sonnet 4 | https://www-cdn.anthropic.com/6d8a8055020700718b0c49369f60816ba2a7c285/Claude%204%20System%20Card.pdf ("May 2025"; revised Jul 16 and Sep 2, 2025) | 104–116 (7.3 Autonomy) | input hash `6be99a52...` is the original; revision adds a changelog and footnotes only |
| Claude Opus 4.1 | https://www-cdn.anthropic.com/9fa30625273bafdf5af82c93719d7ca606485a16/Claude%204.1%20System%20Card.pdf ("August 2025"; revised Sep 15) | 3–6, 20–23 (6.4 Autonomy) | unchanged |
| Claude Sonnet 4.5 | https://www-cdn.anthropic.com/963373e433e489a87a10c823c52a0a013e9172dd/Claude%20Sonnet%204.5%20System%20Card.pdf ("September 2025"; revised Oct 10, Dec 3) | 7, 12–16, 138–149 (9.3 AI R&D) | input had the landing-page URL; replaced with the PDF it resolves to |
| Claude Haiku 4.5 | https://www-cdn.anthropic.com/7aad69bf12627d42234e01ee7c36305dc2f6a970/Claude%20Haiku%204.5%20System%20Card.pdf ("October 2025") | 3–8, 36–39 | as above |
| Claude Opus 4.5 | https://www-cdn.anthropic.com/bf10f64990cfda0ba858290be7b8cc6317685f47/Claude%20Opus%204.5%20System%20Card.pdf ("November 2025"; revised Nov 24, 25, Dec 5) | 7, 12–20 (1.2.4, 2.3–2.5), 133–142 (7.3) | text identical to `assets.anthropic.com/m/64823ba7...` in the input |
| Claude Opus 4.6 | https://www-cdn.anthropic.com/6a5fa276ac68b9aeb0c8b6af5fa36326e0e166dd/Claude%20Opus%204.6%20System%20Card.pdf ("February 2026"; revised Feb 6, 10, 17) | 8, 13–20, 183–195 (8.3) | input hash `14e4fb01...` is the Feb 6 revision; Feb 17 revision changes only HLE/MMMU-Pro figures and adds Sabotage Risk Report links |
| Claude Sonnet 4.6 | https://www-cdn.anthropic.com/bbd8ef16d70b7a1665f14f306ee88b53f686aa75/Claude%20Sonnet%204.6%20System%20Card.pdf ("February 17, 2026"; revised Mar 6) | 6, 10–16, 110–119 (6.3) | input hash `78073f73...` is the original; revision changes BrowseComp only. Still prints the 16.53x LLM-training value the Fable 5 card calls an error |
| Claude Mythos Preview | https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf ("April 7, 2026"; revised Apr 8, 14) | 2–5, 8, 10–14, 18–19, 34–46 (2.3 Autonomy), 188–190 (6.3–6.5) | input had a guessed landing-page URL; confirmed PDF. Title is "System Card: Claude Mythos Preview" |
| Claude Opus 4.7 | https://www-cdn.anthropic.com/037f06850df7fbe871e206dad004c3db5fd50340/Claude%20Opus%204.7%20System%20Card.pdf ("April 16, 2026") | 2, 4, 8, 14, 26–33 (2.3), 191–193 (8.1–8.3) | unchanged |
| Claude Opus 4.8 | https://www-cdn.anthropic.com/0f0c97ad20d8005706296bd92aa1c27c6b2f4f61/Claude%20Opus%204.8%20System%20Card.pdf ("May 28, 2026"; revised Jun 3, 17) | 2–6, 9, 31–32, 42 (2.3), 131, 194–197 (8.1–8.4) | input hash `0b491591...` is the Jun 3 revision; Jun 17 revision corrects virology and prompt-injection figures only |
| Claude Fable 5 / Mythos 5 | https://www-cdn.anthropic.com/57a52ea7d8f0e54e8a542e908266086df425cdf5/Claude%20Fable%205%20&%20Claude%20Mythos%205%20System%20Card.pdf ("June 9, 2026"; revised Jun 11, 25) | 2–6, 10–12, 16–17, 36–53 (2.3), 62, 169, 251–255 (8.1–8.4) | input had a guessed landing-page URL; confirmed PDF (all three landing slugs resolve to it) |
| Claude Sonnet 5 | https://www-cdn.anthropic.com/283ef97c476cf442c91d9a37d5b214242a55bb92/Claude%20Sonnet%205%20System%20Card.pdf ("June 30, 2026"; revised Jul 10) | 2–4, 6, 24–26 (2.3), 33, 114–115 (8.1–8.3) | the two input hashes (`480e0bb5...`, `9e6a1044...`) are earlier revisions differing only in GDPval-AA Elo values and a footnote |
| Claude Opus 5 | https://www-cdn.anthropic.com/ceaf5c7ff2783855203fde8208ec311252dced5b/Claude%20Opus%205%20System%20Card.pdf ("July 24, 2026"; revised Aug 19) | 2–5, 28–33 (2.3), 39, 42, 147–149, 152 (8.1–8.5) | input hash `c5fbac3f...` is the original; revision adds bug-bounty and Cowork results |
| Claude Fable 5.1 / Mythos 5.1 | https://www-cdn.anthropic.com/0339e6a7c5c7b87f5c07798616dc32c215d14235/Claude%20Fable%205.1%20&%20Claude%20Mythos%205.1%20System%20Card.pdf ("September 1, 2026") | 2, 6, 9, 11, 17, 34–42 (2.3), 50–51, 167–172 (8.1–8.7) | unchanged |

Non-card documents used (for rows the cards do not contain):

- Launch posts: anthropic.com/news/claude-3-7-sonnet, /claude-4, /claude-opus-4-1, /claude-sonnet-4-5, /claude-haiku-4-5, /claude-3-5-sonnet; anthropic.com/research/swe-bench-sonnet.
- METR, "Details about METR's preliminary evaluation of Claude 3.5 Sonnet" (Oct 2024), https://metr.org/evaluations/claude-3-5-sonnet-report/
- METR, "Details about METR's preliminary evaluation of Claude 3.7" (4 Apr 2025), https://metr.org/evaluations/claude-3-7-report/

`card_date` was kept at month granularity (YYYY-MM) for column consistency; exact title-page dates are in the table above. All input month values were correct.

## 2. Rows corrected (card contradicted the input)

| Model | Row | Was | Now (card) |
|---|---|---|---|
| Claude 3.7 Sonnet | "Internal general-autonomy time horizon" 55 min | attributed to the card | Not in the card. It is METR's GAC 50% time horizon (METR 3.7 report). Renamed to "METR general autonomy time horizon", family `metr_external`. |
| Claude 3.7 Sonnet | RE-Bench "comparable to median human at 8 h; 32 h budget" | attributed to the card; note said the *card* called it "impressive" | This is METR's own result (5-task subset). The card's RE-Bench result is different: a 4-task modified subset, average normalised score 0.2386, "well below human performance" (added as its own row). The "impressive AI R&D capabilities" phrase is METR's. |
| Claude Opus 4 | Novel compiler 74.4% basic / 6.81% advanced | | 64.44% / 9.44% (card 7.3.3.6). The input values are Opus 4.1's. This also resolves the Opus 4.1 "possibly carried over" flag: 74.4/6.81 are Opus 4.1's own numbers. |
| Claude Opus 4 | Suite 2 "value not surfaced" | | 0.355 (Sonnet 4 0.365, Sonnet 3.7 0.440; threshold 0.6). |
| Claude Sonnet 4 | Suite 1 "below Opus 4; values not surfaced" (memory) | | Per-task values added; Sonnet 4 actually beat Opus 4 on text-based RL (0.675 vs 0.625) and time-series (hard MSE 5.8 vs 6.15), and lost on kernel, LLM training, quadruped, compiler. |
| Claude Opus 4.1 | Kernel "slightly below Opus 4" | | 58.47x best on hard variant (vs 72.65x). |
| Claude Sonnet 4.5 | Kernel "near threshold" | | 108.64x best on hard variant, "crossing above the evaluation-specific threshold on the hard variant for the first time" (threshold 100x). |
| Claude Sonnet 4.5 | Suite 2 "value not surfaced" | | 0.514 (Opus 4.1 0.507, Sonnet 4 0.403). |
| Claude Sonnet 4.5 | Survey "results not surfaced" | | 0/7 say it automates a junior ML researcher; uplift estimates ~100%, 40%, 30%, 20%, 20%, 15%; 4 of 7 attributed most of the boost to Claude Code. Split into productivity and drop-in rows. |
| Claude Opus 4.5 | Kernel "passed, first model to do so" | | 252.42x; first to cross **200x** (Sonnet 4.5's best run had already crossed 100x). |
| Claude Opus 4.5 | Time-series "slightly short (easy); slightly above (hard)" | | Reversed: easy MSE 5.66 beat the 5.8 baseline (met); hard 5.71 did not beat the 5.3 baseline (not met). |
| Claude Opus 4.5 | Text-RL / LLM training / Quadruped rows with no numbers | | 0.975 best; 16.53x; 19.48 / 19.16 (threshold 12). |
| Claude Opus 4.6 | Text-based RL "20.96 and 21.99 in two variants (threshold 12)" (flagged tentative) | | Those are the **Quadruped RL** results (no-hyperparameter / no-reward-function variants, threshold 12 ≈ 4 h). Text-based RL for Opus 4.6 is 0.975 best (threshold 0.9), with the mean above threshold for the first time. Quadruped row added. |
| Claude Opus 4.6 | Kernel score 427 | | Restructured: score is now 190x (standard scaffold) for cross-model comparability; 427x (experimental scaffold) kept in `score_text`. Both are in the card. |
| Claude Opus 4.6 | Novel compiler "below 90%" | | 98.2% basic; 65.83% complex. |
| Claude Opus 4.6 | Drop-in survey score "2/16"; note said the Opus 4.7 card summarised it as 0/16 | | The Opus 4.6 card itself (8.3 results summary) says 0 of 16 after the five affirmative respondents were contacted; raw split (2 already / 3 likely / 11 unlikely) kept in `score_text`. |
| Claude Mythos Preview | Suite 2 "clears 4 h and 8 h thresholds on all tasks; 40 h on 2 of 3" | | That sentence describes Suite 1 (Table 2.3.3.A). Suite 2 is 0.65 (threshold 0.6). Suite 1 summary and per-task rows added. |
| Claude Mythos Preview | LLM training 52x | | 51.91x as printed; the Opus 4.7 card corrects this to 61.79x (aggregation bug); Fable 5 fixed-CPU re-run 60.81x. |
| Claude Opus 4.7 | Drop-in survey "most do not expect a full drop-in L4; about even odds on week-long ambiguous tasks" | | No survey was run on Opus 4.7; the card re-reports the Mythos Preview n=18 survey (1/18 already; 4/18 50% within 3 months). The "even odds" claim is only in a figure and could not be checked. |
| Claude Fable 5 / Mythos 5 | Terminal-Bench 2.1 "88.0%, Fable 5" | | 88.0% is Mythos 5; Fable 5 is 84.3% (20.9% of trials hit a safety refusal and fell back to Opus 4.8). Harness is mini-SWE-agent, not Terminus-2. |
| Claude Fable 5 / Mythos 5 | Acceleration row `source_url` pointed at the Sonnet 5 card | | Points at the Fable 5 card (2.3.6). |
| Claude Sonnet 5 | SWE-bench Verified blank ("72.7% or 85.2%") | | 85.2% (card 8.2). |
| Claude Opus 5 | SWE-bench Verified "not reported by Anthropic" | | 96.0% (card 8.2 text; not in the summary table). |
| Claude Opus 5 | Terminal-Bench 89.1% v2.1 | | Not in the card. The card reports FrontierBench v0.1 (Terminal-Bench successor) 44.4% instead (added). The Fable 5.1 card gives Opus 5 on TB 4.0 (52.3%) and TB-Science (29.0%) (added). |
| Claude Opus 4.8 | Survey row `source_url` was a vellum.ai blog | | Points at the card. |

Confirmed-as-written (confidence upgraded, no value change) — highlights: Opus 4 text-RL 0.625, LLM 2.993x, kernel 72.65x, quadruped 1.25; Opus 4.1 all six Suite 1 values incl. compiler 74.4/6.81; Sonnet 4.5 LLM 5.5x; Opus 4.5 Suite 2 0.604, survey median 100% / mean 220% / 9 of 18, 0/18, SWE-bench 80.9%, TB 2.0 59.3% (was memory); Opus 4.6 Suite 2 0.6124, LLM 34x, survey mean 152%, SWE-bench 80.8%, TB 65.4%; Sonnet 4.6 79.6% / 59.1% and determination (was memory); Mythos Preview 93.9% / 82% / 399.42x / 1 of 18 / ~4x; Opus 4.7 87.6% / 69.4% / 64.3%; Opus 4.8 88.6% / 74.6% / 69.2%; Fable 5 95.0 / 95.5 and Pro 80.0 / 80.3; Fable 5 TB 4.0 42.0% and TB-Science 24.7% (from the Fable 5.1 card); Sonnet 5 TB 2.1 80.4%, Pro 63.2%; Fable 5.1 TB 4.0 55.8%, TB-Science 52.6%, both METR rows, "not reported" for SWE-bench Verified; all threshold-determination wordings.

## 3. Rows added (94)

- **SWE-bench Verified hard subset (RSP checkpoint)** for every card that reports it: 3.7 Sonnet 9.65/42; Opus 4 16.6/42; Sonnet 4 15.4/42; Opus 4.1 18.4/42; Sonnet 4.5 20.4/45; Haiku 4.5 16.45/45; Opus 4.5 21/45; Opus 4.6 21.24/45; Sonnet 4.6 21.7/45 (threshold >50%, i.e. 22.5/45).
- **METR data deduplication** (checkpoint task; family `other`): 3.7 Sonnet 4/30 trials; Opus 4 15/46 (threshold crossed); Sonnet 4 8/29.
- **Suite 1 per-task rows**: 3.7 Sonnet (kernel ~16x and quadruped 0.08 as cited in the Claude 4 card; LLM-training single run >7x); Opus 4 time-series; Sonnet 4 all six; Opus 4.1 time-series 6.541; Sonnet 4.5 time-series 5.91/5.30, text-RL 0.850, quadruped 1.302, compiler 81.7/29.7; Opus 4.5 compiler 93.7/69.37; Opus 4.6 quadruped 20.96/21.99 and time-series 5.86/5.76; Sonnet 4.6 all six; Mythos Preview summary + TS 4.55, quadruped 30.87, compiler 77.2; Opus 4.7 all five unbounded tasks; Opus 4.8 LLM training 32.64x (from the Fable 5 re-run) and a "no longer reported" summary; Fable 5 / Mythos 5 all five (kernel 430.93x, TS 4.51, LLM 69.61x, quadruped 29.54, compiler 85.3%); Sonnet 5 all five (284.52x, 5.80, 26.49x, 19.94, 76.1%); Opus 5 all five plus the new LLM-training hard variant 14.19x (449.46x, 5.68, 68.54x, 31.3, 80.91%); Fable 5.1 "not run".
- **Suite 2**: 3.7 Sonnet 0.440 (from the Claude 4 card); Sonnet 4 0.365; Opus 4.1 not run; Sonnet 4.6 not reported; Opus 4.7 did not run.
- **Surveys**: Opus 4 (0/4; "some productivity gains"); Opus 4.1 not run; Sonnet 4.5 drop-in 0/7; Opus 4.7 no new survey; Fable 5, Sonnet 5, Opus 5, Fable 5.1 no survey (with what replaced it).
- **Internal AI R&D acceleration measure**: Opus 4.6 (8.3.5 preliminary metrics); Mythos Preview (AECI slope ratio 1.86x–4.3x; progress multiplier <2x); Opus 4.7 (no sustained 2x); Opus 4.8 (AECI between 4.7 and Mythos Preview); Fable 5.1 (CoBench row; cross-cutting metrics row with AECI 161.98).
- **METR external evaluation**: Mythos Preview (4 of 5 insights rediscovered; partner not named); Fable 5 / Mythos 5 (38 hardest tasks; "likely unable to fully and reliably automate R&D for frontier projects spanning multiple weeks").
- **Other benchmark rows**: Sonnet 4 80.2% parallel-compute SWE-bench (launch post); Opus 4.1 Terminal-bench 46.5% and Sonnet 4.5 50.0%/51.0% as listed in the Opus 4.5 / Opus 4.6 card tables; Mythos Preview SWE-bench Pro 77.8%; Opus 5 SWE-bench Pro 79.2%, FrontierBench v0.1 44.4%, TB 4.0 52.3%, TB-Science 29.0%; Fable 5.1 SWE-bench Pro 81.2%; 3.5 Sonnet (Oct 2024) determination.

## 4. Threshold / human-hours mapping as stated in the cards (for reference)

- Kernel optimisation: threshold 100x; 4x ≈ 1 h, 200x ≈ 8 h (Opus 4.5 card), 300x ≈ 40 h (Opus 4.6 card onward). Earlier cards used 4x–100x by variant; the multicore/vec variants were dropped in the Opus 4.5 card as unreliable.
- Time-series forecasting: hard-variant human baseline MSE 5.3 ≈ 40 h (Mythos Preview table); the 5.8 baseline is called "easy ≈ 4 h" in the Opus 4.5 card and "medium ≈ 8 h" in the Opus 4.6 and Sonnet 4.6 cards.
- Text-based RL: 0.9 ≈ 8 h. LLM training: 4x ≈ 4–8 h. Quadruped RL: 12 ≈ 4 h (normalised to 1 in plots). Novel compiler: 90% of complex tests ≈ 40 h.
- Suite 2 rule-out threshold: 0.6 (Claude 4 card onward). Survey rule-out (Claude 4 to Opus 4.5): under half say it automates a junior ML researcher and median boost <3x.
- Threshold naming: "ASL-4 autonomy" (Claude 4 card) → "AI R&D-4" (Sonnet 4.5 to Sonnet 4.6) → "automated AI R&D threshold" under RSP v3.x (Mythos Preview onward: substitute for all Research Scientists/Engineers at competitive cost, or dramatic ≈2x acceleration).

## 5. Known inconsistencies between cards (kept in `notes`)

- LLM training: Opus 4.6 card prints 34x (also in the Mythos Preview table) but the Fable 5 re-run table lists its "published" value as 30.09x. Mythos Preview card prints 51.91x, Opus 4.7 card corrects it to 61.79x, Fable 5 table lists 42.42x as "published". Opus 4.7 card prints 40.81x, Fable 5 table lists 34.77x. Sonnet 4.6 card prints 16.53x, which the Fable 5 card says is an error (22.33x).
- Later cards re-quote earlier models at different values (re-runs): e.g. Sonnet 4.5 card cites Opus 4 kernel 48.92x (vs 72.65x printed), Opus 4 quadruped 0.769 (vs 1.25), Opus 4.1 text-RL 0.475 (vs 0.425), Opus 4.1 LLM 2.5x (vs 2.837x). Opus 4.7 quadruped 26.5 and compiler 71.1% become 24.73 and 70.4% in the Fable 5 / Sonnet 5 tables.
- Terminal-Bench version labelling: the Opus 4.5 card table lists Sonnet 4.5 50.0% and Opus 4.1 46.5% under "Terminal-bench 2.0", while the Opus 4.6 card gives Sonnet 4.5 51.0% on TB 2.0; the 50.0% matches the Sonnet 4.5 launch (pre-2.0).

## 6. Still unverified

- Claude 3.7 Sonnet SWE-bench Verified 62.3% (full 500) — `snippet`. Not in the card; the launch-post text gives 63.7% on a 489-task subset without the scaffold and 70.3% with it; 62.3% is only in the post's chart image.
- Claude Sonnet 4 Terminal-bench 35.5% (and 41.3% with parallel compute) — `memory`. Not in the card or the launch-post text (chart only).
- Claude Opus 4.1 Terminal-Bench 43.3% — `memory`. Not in the card or the launch-post text. The Opus 4.5 card's 46.5% for Opus 4.1 is recorded as a separate `reported` row.
- Claude Opus 4 "50.0% Terminal-bench with parallel test-time compute" — left as a note only; not in the post text.
- The Opus 4.7 per-dimension survey results (Figure 2.3.5.A) and the Fable 5.1 CoBench absolute scores (Figure 2.3.4.1.A) exist only as figures; not readable from extracted text.
- The "When AI builds itself" (Jun 2026) poll figure previously in the Mythos Preview productivity note is retained as unverified; the Fable 5.1 card only names the publication.
- RE-Bench per-task numbers: no Anthropic card prints them. The only card-reported RE-Bench result is the 3.7 Sonnet aggregate (0.2386 on a 4-task subset); no card after 3.7 Sonnet mentions RE-Bench. METR's 3.5 Sonnet report gives task names (progress on "optimize a kernel", "GPT-2 Chat RL", "scaffolding for rust codecontests") but no card-comparable scores.

---

# Part B: snippet-only collection (pass 1)

# GDM AI R&D benchmark compilation — notes (compiled 2026-09-13)

Environment: WebFetch/curl blocked; WebSearch only. The session's WebSearch budget was
exhausted (200/200) after ~40 queries in this task, so ~10 planned confirmation queries
were never run (listed under Open questions). Rows marked `confidence=memory` were
not confirmed by any snippet.

## Cards / reports covered (in release order)

| Model | Card date | Document | URL |
|---|---|---|---|
| Gemini 1.5 Pro | 2024 | Gemini 1.5 tech report (dangerous-capability evals; no ML R&D) | https://arxiv.org/pdf/2403.05530 |
| Gemini 2.0 Flash | card published 2025-04-15 | Gemini 2.0 Flash Model Card | https://modelcards.withgoogle.com/assets/documents/gemini-2-flash.pdf |
| Gemini 2.5 Pro Preview | 2025-04-16 (upd. 2025-05-09) | Gemini 2.5 Pro Preview Model Card | https://storage.googleapis.com/model-cards/documents/gemini-2.5-pro-preview.pdf |
| Gemini 2.5 Pro GA | 2025-06-27 | Gemini 2.5 Pro Model Card | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-2-5-Pro-Model-Card.pdf |
| Gemini 2.5 (family) | 2025-06/07 | Gemini 2.5 tech report, "Frontier Safety" section | https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf (arXiv 2507.06261) |
| Gemini 2.5 Deep Think | 2025-08-01 | Gemini 2.5 Deep Think Model Card | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-2-5-Deep-Think-Model-Card.pdf |
| Gemini 2.5 Computer Use | 2025-10-07 | Gemini 2.5 Computer Use Model Card | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-2-5-Computer-Use-Model-Card.pdf |
| Gemini 3 Pro | 2025-11-18 | Gemini 3 Pro Model Card | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf |
| Gemini 3 Pro | 2025-11 | Gemini 3 Pro Frontier Safety Framework Report | https://storage.googleapis.com/deepmind-media/gemini/gemini_3_pro_fsf_report.pdf |
| Gemini 3 Deep Think | 2025-12 (V2 Feb 2026) | No standalone card found; Gemini 3 Pro card Deep Think addendum | https://deepmind.google/models/model-cards/gemini-3-pro/ |
| Gemini 3 Flash | 2025-12-17 | Gemini 3 Flash Model Card | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Flash-Model-Card.pdf |
| Gemini 3.1 Pro | 2026-02 (Feb 19) | Gemini 3.1 Pro Model Card (full FSF eval, Deep Think focus) | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-1-Pro-Model-Card.pdf |
| Gemini 3.1 Flash-Lite | early 2026 | Gemini 3.1 Flash-Lite Model Card | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-1-Flash-Lite-Model-Card.pdf |
| Gemini 3.5 Flash | 2026-05 (GA May 19, I/O) | Gemini 3.5 Flash Model Card | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-5-Flash-Model-Card.pdf |
| Gemini 3.5 Flash-Lite / 3.5 Flash Cyber | mid 2026 | Model cards (no ML R&D content) | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-5-Flash-Lite-Model-Card.pdf |
| Gemini 3.5 Pro | NOT RELEASED (announced I/O 2026-05-19; GA slipped June/July/Jul 17) | none | — |
| Gemini 3.6 Flash | 2026-07-21 | Gemini 3.6 Flash Model Card | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-6-Flash-Model-Card.pdf |
| Gemini 3.7 Flash | 2026-08-13 | Gemini 3.7 Flash Model Card + Gemini 3.7 Flash FSF Report (Aug 2026) | https://storage.googleapis.com/deepmind-media/gemini/gemini_3-7_flash_fsf_report.pdf |
| Gemini 3.8 Flash (+3.8 Flash Cyber) | 2026-09-02 | Gemini 3.8 Flash Model Card | https://deepmind.google/models/model-cards/gemini-3-8-flash/ |

Framework context surfaced by search: FSF v2 (Feb 2025) used "Machine Learning R&D
Autonomy Level 1" (and Uplift Level 1); FSF v3 (Sep 2025) renamed to "ML R&D acceleration
level 1" / "automation level 1" and added harmful manipulation; FSF April-2026 update
(v3.1) added Tracked Capability Levels (TCLs) — later cards say "no T/CCLs reached".

## Headline ML R&D numbers (RE-Bench, human-normalized average)

- Gemini 2.5 Pro (preview and GA): best runs 50%–125% of best human-written solution per
  task; average below human baseline; two tasks' best runs exceeded best human reference;
  early-warning threshold not reached. Alert threshold "set above human performance".
- Gemini 3 Pro: 1.04 (as quoted in the 3.1 Pro card). FSF report methodology: 7 envs,
  16 attempts/task aggregated to a 32-hour total time budget, 95% CI from 24 runs,
  humans = 71 eight-hour attempts by 61 experts. Better than 2.5 mainly on Scaling Law
  Experiment and Optimize LLM Foundry; "substantially below the alert threshold for both
  acceleration and automation".
- Gemini 3.1 Pro (Deep Think mode): 1.27; Optimise LLM Foundry 300s -> 47s vs human 94s;
  "average across all RE-Bench challenges remains below the alert threshold"; Zvi:
  GDM says model "too inconsistent to qualify".
- Gemini 3.5/3.6/3.7/3.8 Flash: no new RE-Bench number surfaced; cards defer to
  3.1 Pro (3.5, 3.6) or to 3.7 Flash (3.8). 3.7 Flash has its own FSF report whose
  ML R&D content was not visible in snippets.

## Queries that worked (produced usable snippets)

- "Gemini 3.1 Pro model card RE-Bench 1.27 Deep Think ML R&D"
- "Gemini 3 Pro Frontier Safety Framework report RE-Bench score machine learning R&D"
- "\"Gemini 3 Pro\" FSF report RE-Bench \"human-normalized\" alert threshold hours time budget"
  (gave the 16 attempts / 32-hour / 24-run methodology)
- "Gemini 2.5 Pro model card Frontier Safety machine learning R&D CCL RE-Bench"
- "Gemini 2.5 Pro Preview model card \"Figure 4\" RE-Bench \"Key results\" ... METR methodology"
- "Gemini 3 Pro model card SWE-bench Verified 76.2 Terminal-Bench 2.0 54.2 LiveCodeBench Pro Elo"
- "Gemini 3.1 Pro SWE-bench Verified 80.6 Terminal-Bench 2.0 68.5 LiveCodeBench Pro 2887"
- "Gemini 2.5 Pro model card SWE-bench Verified 63.8 67.2 Aider Polyglot 82.2 LiveCodeBench"
- "Gemini 3.5 Flash model card May 2026 frontier safety machine learning R&D RE-Bench"
  (revealed the 3.5/3.6/3.7/3.8 Flash card series)
- "Gemini 3.6 Flash model card frontier safety ..." / "Gemini 3.7 Flash model card frontier safety ..."
- "Gemini 3.8 Flash model card September 2026 frontier safety CCL ... Terminal-Bench 2.1 90.8"
- "\"Gemini 3.5 Pro\" release model card September 2026" (confirmed not shipped)
- "Zvi \"Gemini 3\" model card safety framework RE-Bench ... acceleration automation"
- "\"Gemini 3 Deep Think\" \"model card\" storage.googleapis.com deepmind-media"
  (gave the "Deep Think mode ... consistent with the original Gemini 3 Pro safety assessment" line)
- "Gemini 1.5 Pro technical report frontier safety dangerous capability evaluations ..."

Queries that did not help: anything asking for the Gemini 2.0 Pro Experimental card's
FSF text; "Gemini 3 Deep Think model card December 2025 ..." (only launch coverage);
Gemini 3.7 Flash FSF report ML R&D content (report indexed but ML R&D lines not in snippet).

## Open questions / unconfirmed numbers

1. Gemini 3 Pro FSF report: per-task RE-Bench scores (only in a figure); whether 1.04 was
   computed under the 32-hour/16-attempt protocol; whether any internal ML R&D task suite
   results were reported (none surfaced).
2. Gemini 3.1 Pro card: time budget / attempts behind the 1.27 Deep Think figure; whether
   a non-Deep-Think RE-Bench figure was given; exact "inconsistent" wording.
3. Gemini 3.7 Flash FSF report (Aug 2026): does it contain a new RE-Bench / ML R&D score
   or TCL determination for ML R&D? Not visible in snippets.
4. Gemini 2.5 Deep Think card: ML R&D section wording (recorded from memory).
5. Gemini 2.5 Computer Use card: FSF deferral wording (memory).
6. Gemini 2.0 Flash card: CCL determination wording (memory); no Gemini 2.0 Pro card found.
7. Gemini 2.5 Pro single-attempt SWE-bench Verified 59.6% and 03-25 63.8% (memory).
8. Gemini 3 Flash Terminal-Bench 2.0 47.6% (memory); its FSF deferral wording (memory).
9. Gemini 3.7 Flash Terminal-Bench 2.1: 81.6% (two sources) vs 85.8% (one) — unresolved.
10. Gemini 3.5 Flash SWE-bench Verified 78.8 comes from an aggregator, not confirmed as card.
11. Gemini 3.5 Flash card date: snippet says PDF dated May 1 2026 vs May 19 launch.
12. "Gemini Pro received 73% on the RE-Bench" (Trustible) — provenance unknown; ignored.
13. SWE-bench Verified for Gemini 3.6/3.7/3.8 Flash cards: cards appear to have switched
    to SWE-Bench Pro / DeepSWE; Verified figures not surfaced.

---

# OpenAI system cards — AI R&D / self-improvement benchmark scrape notes

Compiled 2026-09-13. Companion file: `openai.csv` (124 rows; 103 tagged `snippet`, 21 tagged `memory`; 51 rows carry a numeric score).

Environment constraint: WebFetch/curl blocked for all relevant hosts; WebSearch only. The session-wide WebSearch budget (200) was exhausted after ~70 queries from this task, so a final planned batch (Astra numbers, GPT-5.6 revised-suite numbers, GPT-5.2/5.2-Codex/5.3-Codex/5.4 per-benchmark values, o3/o4-mini, GPT-4.5, deep research, o1-preview, gpt-oss values) could not run. Those gaps are listed under Open questions.

## Cards covered (chronological)

| # | Card | Date | URL |
|---|------|------|-----|
| 1 | GPT-4o System Card | 2024-08-08 | https://cdn.openai.com/gpt-4o-system-card.pdf |
| 2 | OpenAI o1 System Card (o1-preview / o1-mini) | 2024-09-12 | https://cdn.openai.com/o1-system-card.pdf |
| 3 | OpenAI o1 System Card | 2024-12-05 | https://cdn.openai.com/o1-system-card-20241205.pdf (arXiv 2412.16720) |
| 4 | OpenAI o3-mini System Card | 2025-01-31 | https://cdn.openai.com/o3-mini-system-card-feb10.pdf |
| 5 | Deep Research System Card | 2025-02-25 | https://cdn.openai.com/deep-research-system-card.pdf |
| 6 | GPT-4.5 System Card | 2025-02-27 | https://openai.com/index/gpt-4-5-system-card/ |
| 7 | OpenAI o3 and o4-mini System Card | 2025-04-16 | https://cdn.openai.com/pdf/2221c875-02dc-4789-800b-e7758f3722c1/o3-and-o4-mini-system-card.pdf |
| 8 | Addendum to o3/o4-mini card: Codex (codex-1) | 2025-05-16 | https://cdn.openai.com/pdf/8df7697b-c1b2-4222-be00-1fd3298f351d/codex_system_card.pdf |
| 9 | ChatGPT Agent System Card | 2025-07-17 | https://cdn.openai.com/pdf/6bcccca6-3b64-43cb-a66e-4647073142d7/chatgpt_agent_system_card_launch.pdf |
| 10 | gpt-oss-120b & gpt-oss-20b Model Card | 2025-08-05 | https://cdn.openai.com/pdf/419b6906-9da6-406c-a19d-1bb078ac7637/oai_gpt-oss_model_card.pdf (arXiv 2508.10925) |
| 11 | GPT-5 System Card | 2025-08-07 (rev. 08-13) | https://cdn.openai.com/gpt-5-system-card.pdf (arXiv 2601.03267) |
| 12 | Addendum to GPT-5 card: GPT-5-Codex | 2025-09-15 | https://cdn.openai.com/pdf/97cc5669-7a25-4e63-b15f-5fd5bdc4d149/gpt-5-codex-system-card.pdf |
| 13 | GPT-5.1 Instant & Thinking System Card Addendum | 2025-11-12 | https://cdn.openai.com/pdf/4173ec8d-1229-47db-96de-06d87147e07e/5_1_system_card.pdf |
| 14 | GPT-5.1-Codex-Max System Card | 2025-11-18 | https://cdn.openai.com/pdf/2a7d98b1-57e5-4147-8d0e-683894d782ae/5p1_codex_max_card_03.pdf |
| 15 | Update to GPT-5 System Card: GPT-5.2 | 2025-12-11 | https://cdn.openai.com/pdf/3a4153c8-c748-4b71-8e31-aecbde944f8d/oai_5_2_system-card.pdf |
| 16 | Addendum to GPT-5.2 card: GPT-5.2-Codex | 2025-12-18 | https://cdn.openai.com/pdf/ac7c37ae-7f4c-4442-b741-2eabdeaf77e0/oai_5_2_Codex.pdf |
| 17 | GPT-5.3-Codex System Card | 2026-02-05 | https://cdn.openai.com/pdf/23eca107-a9b1-4d2c-b156-7deb4fbc697c/GPT-5-3-Codex-System-Card-02.pdf |
| 18 | GPT-5.4 Thinking System Card | 2026-03-05 | https://deploymentsafety.openai.com/gpt-5-4-thinking/gpt-5-4-thinking.pdf |
| 19 | GPT-5.5 System Card | 2026-04-23 | https://deploymentsafety.openai.com/gpt-5-5/gpt-5-5.pdf |
| 20 | GPT-5.5 Instant System Card | 2026-05-04 | https://deploymentsafety.openai.com/gpt-5-5-instant/gpt-5-5-instant.pdf |
| 21 | GPT-5.6 Preview System Card (Sol/Terra/Luna) | 2026-06-25 | https://deploymentsafety.openai.com/gpt-5-6-preview/gpt-5-6-preview.pdf |
| 22 | GPT-5.6 System Card | 2026-07-09 | https://deploymentsafety.openai.com/gpt-5-6/gpt-5-6.pdf |
| 22b | GPT-5.6 August Updates | 2026-08-06 | https://cdn.openai.com/pdf/GPT_5_6_August_Updates.pdf (not mined) |
| 23 | GPT-6 Astra System Card | 2026-09-03 | https://deploymentsafety.openai.com/gpt-6-astra |

Not covered / not applicable: Operator (Jan 2025) and o3 Operator addendum (computer-use; no self-improvement evals); GPT-4.1 (no system card); "GPT-5.4" non-Thinking variants (single card); "o5" does not exist as a card — the post-o4 line was folded into GPT-5.x.

Naming shift: cards up to GPT-4.5 use "Model autonomy" (Low/Medium/High/Critical risk). From o3/o4-mini (Preparedness Framework v2, Apr 2025) the category is "AI Self-improvement" with a High capability threshold defined (per 5.4/5.5 cards) as "equivalent to a performant mid-career research engineer" and Critical as fully automating self-improvement. Every card through GPT-5.6 states the model is below High for AI self-improvement; Astra's designation was not confirmed.

## Headline numeric trajectory recovered from snippets

| Model | SWE-bench Verified | SWE-Lancer IC Diamond | OpenAI PRs | MLE-bench-30 (bronze+) | PaperBench(-10) | OpenAI-Proof Q&A | METR 50% horizon |
|---|---|---|---|---|---|---|---|
| o1-preview (Dec card) | 41.3% (Agentless, 5 tries) | – | – | 37% pass@10 (full MLE-bench) | – | – | – |
| o1 | 40.9% | – | – | 27% pre / 24% post pass@10 | – | 36% agentic tasks | ~human 2h (adapted scaffold) |
| o3-mini | 39% Agentless / 61% internal tools | – | ~0% ("failed entirely") | "doesn't impress" | – | 27% agentic tasks; RE interview 93% coding / 80% MCQ | – |
| o3 / o4-mini | 69.1% / 68.1% | – | – | – | ~24% (ambiguous) | – | 1h30m (o3) |
| ChatGPT agent | ~o3 | – | – | 9% | highest (w/ browsing) | – | – |
| gpt-5-thinking | 74.9% | no improvement | (45%?) | 8% | 24% (from 22%) | 2% | 2h17m |
| GPT-5.1 | – | 67%* | 45%* | 12% | 34% | 2% | – |
| GPT-5.1-Codex-Max | 77.9% | 80% | 53% | 17% | 40% | 8% | 2h40m |
| GPT-5.2 | 80.0% (memory) | (40/237 omitted) | – | 12.2%† | – | – | ~6.6h |
| GPT-5.3-Codex | – | 81.4% | – | not reported | – | – | – |
| GPT-5.4 Thinking | – | – | – | 23% | – | 5.8% | – |
| GPT-5.5 | – | – | – | 37% | – | 1.7% | – |
| GPT-5.6 Sol | – | – | – | 48.0% (revised suite) | – | – | not robust (cheating) |
| GPT-6 Astra | – | – | – | – | – | – | – |

\* "from 67%" / "from 45%" baselines in the Codex-Max card may refer to GPT-5.1-Codex rather than GPT-5.1 Thinking.
† 12.2% attributed to GPT-5.2 by inference (Zvi: 5.4 "moved from 12.2% to 23%, though this test wasn't reported by GPT-5.3-Codex").

New evals appearing in 2026 cards: Internal Research Debugging Eval (GPT-5.5 median 50.5%, not significantly above 5.4), Monorepo-Bench (5.4/5.5, "little improvement"), and a "revised suite" including "MLE-bench (revised)" from GPT-5.6 onward.

## Queries that worked (snippet yielded numbers)

- `o1 system card SWE-bench Verified MLE-bench "OpenAI Research Engineer Interview" agentic tasks scores` → 41.3 / 40.9 / 37% pass@10 / 18 coding + 97 MCQ.
- `o3-mini system card "SWE-Lancer" "OpenAI PRs" "MLE-bench" "PaperBench" percent` → 39% Agentless / 61% internal tools.
- `o3-mini system card January 2025 "OpenAI PRs" "MLE-bench" "OpenAI Research Engineer Interview" ...` (surfaced Zvi "o3-mini Early Days") → 93% coding, 80% MCQ, agentic 27% vs 36%, PRs failed, o1 48% w/ tools.
- `GPT-5 system card "OpenAI PRs" "PaperBench" "MLE-bench" gpt-5-thinking percent AI self-improvement high` → 8% MLE-30, 22→24% PaperBench, no SWE-Lancer improvement, "did not meet High".
- `GPT-5.4 Thinking system card OpenAI PRs 60% MLE-bench PaperBench OpenAI-Proof Q&A results March 2026` → OPQA 20 problems, gpt-5-thinking 2%.
- `Zvi GPT-4.5 system card SWE-Lancer OpenAI PRs MLE-bench PaperBench deep research` (domain-restricted to thezvi/lesswrong) → Codex-Max deltas: SWE-Lancer 67→80, PaperBench-10 24→34→40, MLE-30 8→12→17, PRs 45→53, OPQA 2→8.
- `Zvi "GPT 5.5: The System Card" ...` → OPQA 5.8→1.7, MLE-30 23→37.
- `Zvi GPT-5.4 system card self-improvement ...` → MLE-30 12.2→23; 5.3-Codex didn't report MLE.
- `Zvi "GPT-5.6: The System Card" MLE-bench ...` → Sol 48.0% MLE-bench; revised suite.
- `GPT-5.5 system card "AI Self-improvement" "High" threshold ...` → "performant mid-career research engineer"; Internal Research Debugging Eval 50.5%.
- `OpenAI system card METR time horizon 50% GPT-5 GPT-5.1-Codex-Max GPT-5.2 hours cited` → 2h40m; `METR evaluation OpenAI GPT-5.2 ... metr.org` → 2h17m, o3 1h30m, Sol cheating; `Zvi GPT-5.2 system card ...` → 6.6h.
- `"GPT-6" OpenAI system card 2026 Astra release date self-improvement` → Astra exists, Sep 3 2026, Critical cyber.
- `GPT-5.5 Instant system card GPT-5.6 Preview system card AI self-improvement evaluations` → both below High; revised suite statement.
- `codex-1 Codex system card May 2025 ...` → 72.1% / 83.8% (secondary), SAG not-High statement.
- `GPT-5.3-Codex system card February 2026 ...` → SWE-bench Pro 56.8/56.4/55.6, SWE-Lancer 81.4.
- Restricting `allowed_domains` to `deploymentsafety.openai.com` was useful for discovering which cards exist (5.3-Codex, 5.4 Thinking, 5.5, 5.5 Instant, 5.6 Preview, 5.6, Astra) but the hub pages' snippets rarely include numbers.

Queries that did not work: anything asking for GPT-4.5 / deep research / o3-o4-mini / gpt-oss / GPT-5.2 / 5.2-Codex per-benchmark values — snippets return only benchmark descriptions from the PDFs' boilerplate. Zvi's "On GPT-4.5", "We're in Deep Research", "o3 Will Use Its Tools For You" and "The Codex of Ultimate Vibing" posts were found but snippets did not expose the numbers.

## Open questions (numbers not confirmed)

1. **GPT-6 Astra**: AI Self-Improvement designation (High or not?) and every per-benchmark value; METR Astra report / time horizon. Highest-priority gap.
2. **GPT-5.6 (Sol/Terra/Luna)**: composition of the "revised suite" and all values other than Sol MLE-bench 48.0%; meaning of "above the threshold" in that snippet; August Updates doc.
3. **GPT-5.5 / 5.4 Thinking**: SWE-bench Verified, SWE-Lancer Diamond, OpenAI PRs, PaperBench values; Monorepo-Bench and 5.4 Internal Research Debugging Eval values; whether 5.5 card actually re-ran these or copied 5.4 (Zvi suggests copy).
4. **GPT-5.3-Codex, GPT-5.2-Codex, GPT-5.2**: OpenAI PRs, PaperBench-10, SWE-Lancer (197-task variant), OPQA values. GPT-5.2 SWE-bench Verified 80.0% is memory from launch blog, not the card.
5. **GPT-5.1 Thinking vs GPT-5.1-Codex**: which model the Codex-Max card's 67% (SWE-Lancer) and 45% (PRs) baselines refer to; gpt-5-thinking's own OpenAI PRs value.
6. **GPT-5-Codex addendum**: self-improvement values.
7. **gpt-oss**: OpenAI PRs, PaperBench values (card includes them); SWE-bench Verified 62.4% from launch.
8. **ChatGPT agent**: PaperBench-with-browsing value; SWE-Lancer / PRs values.
9. **o3 / o4-mini**: SWE-Lancer $ earned, OpenAI PRs, MLE-bench, PaperBench (24% snippet is a secondary source with ambiguous attribution).
10. **GPT-4.5**: all values except SWE-bench Verified 38% (memory). Card includes SWE-Lancer, OpenAI PRs, MLE-bench, RE interviews, agentic tasks.
11. **deep research**: all values (SWE-bench Verified, SWE-Lancer, PRs, MLE-bench, RE interviews, agentic tasks).
12. **o1-preview Sep 2024 card**: SWE-bench Verified / MLE-bench / RE interview / agentic-task values as printed in that version (Dec card superseded them).
13. **GPT-4o**: RE interview and agentic-task values; METR summary statistic.
14. **o1 Dec card**: per-task agentic pass rates (OpenAI API proxy, Mistral 7B in Docker, buy GPU…), absolute RE-interview values, o1-mini SWE-bench Verified.
15. **SWE-Lancer dollar figures** were never surfaced for any card (cards report $ earned and % on IC SWE Diamond; only percentages surfaced).
16. Whether the GPT-5.2 METR 6.6h figure is cited in the GPT-5.2 card itself or only in METR's own report.

Suggested follow-up when fetch access is available: pull the PDFs listed above (cdn.openai.com / deploymentsafety.openai.com) and read the "AI Self-improvement" (or "Model autonomy") sections directly; each has a summary table with all values.

---

# Anthropic system cards: AI R&D benchmark compilation notes

Compiled 2026-09-13 via WebSearch snippets only (WebFetch/curl blocked; session search budget of 200 calls was exhausted after ~72 queries in this task, so the last planned verification batch of 16 queries did not run). CSV: `anthropic.csv` (114 rows; 103 tagged `snippet`, 11 tagged `memory`).

## Cards covered (in order)

| # | Model(s) | Card date | Card | URL status |
|---|---|---|---|---|
| 1 | Claude 3 Opus | Mar 2024 | Model Card and Evaluations for Claude Models | confirmed CDN URL; no AI R&D evals |
| 2 | Claude 3.5 Sonnet | Jun 2024 | Claude 3.5 Sonnet Model Card Addendum | confirmed |
| 3 | Claude 3.5 Sonnet (upgraded) + 3.5 Haiku | Oct 2024 | Model Card Addendum: Claude 3.5 Haiku and Upgraded Claude 3.5 Sonnet | confirmed |
| 4 | Claude 3.7 Sonnet | Feb 2025 | Claude 3.7 Sonnet System Card | confirmed |
| 5 | Claude Opus 4 / Sonnet 4 | May 2025 | System Card: Claude Opus 4 & Claude Sonnet 4 | confirmed |
| 6 | Claude Opus 4.1 | Aug 2025 | System Card Addendum: Claude Opus 4.1 | confirmed |
| 7 | Claude Sonnet 4.5 | Sep 2025 | System Card: Claude Sonnet 4.5 | anthropic.com slug confirmed |
| 8 | Claude Haiku 4.5 | Oct 2025 | System Card: Claude Haiku 4.5 | anthropic.com slug confirmed |
| 9 | Claude Opus 4.5 | Nov 2025 | System Card: Claude Opus 4.5 | confirmed |
| 10 | Claude Opus 4.6 | Feb 2026 | System Card: Claude Opus 4.6 | confirmed (several CDN hashes exist) |
| 11 | Claude Sonnet 4.6 | Feb 17 2026 | System Card: Claude Sonnet 4.6 | confirmed |
| 12 | Claude Mythos Preview | Apr 2026 | Claude Mythos Preview System Card (244 pp; model not released, Project Glasswing) | **URL is a best guess** |
| 13 | Claude Opus 4.7 | Apr 16 2026 | System Card: Claude Opus 4.7 (232 pp) | confirmed |
| 14 | Claude Opus 4.8 | May 28 2026 | System Card: Claude Opus 4.8 | confirmed |
| 15 | Claude Fable 5 & Claude Mythos 5 | Jun 9 2026 | System Card: Claude Fable 5 & Claude Mythos 5 | **URL is a best guess** |
| 16 | Claude Sonnet 5 | Jun 30 2026 | System Card: Claude Sonnet 5 (144 pp) | confirmed |
| 17 | Claude Opus 5 | Jul 24 2026 | System Card: Claude Opus 5 | confirmed |
| 18 | Claude Fable 5.1 & Claude Mythos 5.1 | Sep 1 2026 | System Card: Claude Fable 5.1 & Claude Mythos 5.1 (212 pp) | confirmed |

No Claude Haiku 4.6 exists (search confirmed). Fable 5.1 and Mythos 5.1 share identical weights and differ only in safeguards; Mythos 5 / Mythos 5.1 are the lighter-safeguard partner-only configurations.

Threshold naming: cards through Opus 4.6 use "AI R&D-4" (RSP v2.2). From Opus 4.7 / Mythos Preview onward the card uses a revised "automated AI R&D capability threshold" (operationalized as: can fully substitute for research scientists/engineers, or produces a sustained AI-attributable 2x acceleration in the pace of progress). Sonnet 5, Opus 5 and Opus 4.8 cards did not run new internal surveys and point back to Mythos 5 sec. 2.3 / Mythos Preview sec. 2.3 / Opus 4.7 sec. 2.3.5.

## Queries that worked best

- `Claude Opus 4 system card "Internal AI Research Evaluation Suite 1" LLM training quadruped RL novel compiler score` -> surfaced per-task Opus 4 / Opus 4.1 numbers and the Opus 5 card statement that only unsaturated/unbounded tasks are still reported.
- `Claude Opus 4.5 system card "Internal AI Research Evaluation Suite 2" score threshold 0.6 AI R&D-4 rule out` -> 0.604 vs 0.6; 0/18 survey.
- `Zvi "Opus 4.5" model card "RE-Bench" "Suite 1" "18 participants" uplift survey productivity percent` -> median 100% / mean 220%.
- `Claude 4 system card AI R&D "internal survey" researchers productivity uplift Opus 4 "AI R&D-4"` -> Opus 4.6 survey (30-700%, mean 152%, median 100%; 11/3/2 of 16 on L4 replacement).
- `Claude Sonnet 4.5 system card AI R&D "Internal AI research evaluation suite 2" score` -> Opus 4.6 Suite 2 = 0.6124.
- `Zvi "Sonnet 4.5" system card "AI R&D" internal survey "Suite" kernel "LLM training" speedup "AI R&D-4"` -> Sonnet 4.5 LLM training 5.5x (first over 4x expert line); list of Suite 1 task sections.
- `Mythos Preview system card AI R&D "Suite 1" OR "Suite 2" ... kernel 399x` -> 399x kernel, 52x LLM training, Table 2.3.3.A (4h/8h all tasks, 40h on 2/3), 1/18 L4 survey, geometric-mean ~4x uplift.
- `Opus 4.6 system card "Suite 1" ... "RE-Bench"` -> 427x kernel (novel scaffold; 300x ~ 40 expert-hours), 34x LLM training vs 4x human line, 20.96 / 21.99 vs threshold 12.
- `kingy "Claude 3.7 Sonnet" system card summary AI R&D "kernel" "RE-Bench" "32 hours" human baseline` -> 32h budget ~ median human 8h on 5-task RE-Bench subset.
- Vellum "benchmarks explained" posts were reliable for SWE-bench Verified / Terminal-Bench numbers for Opus 4.5-4.8, Sonnet 5, Fable 5/Mythos 5.
- Zvi (thezvi.substack / wordpress / lesswrong) writeups exist for every card from 3.7 onward and were the best snippet source for AI R&D section details.

Queries that did not help: anything asking for RE-Bench per-task names ("Optimize LLM foundry", "Fix embedding", "Scaling law experiment") in Anthropic cards; "PaperBench" in Anthropic cards (no hits; PaperBench does not appear to be reported by Anthropic); 3.7 Sonnet Suite 1 per-task numbers.

## Memory-tagged rows (11)

- Opus 4 SWE-bench Verified high-compute 79.4; Opus 4 Terminal-bench high-compute 50.0; Sonnet 4 SWE-bench high-compute 80.2; Sonnet 4 Terminal-bench 35.5 (41.3 high-compute); Opus 4.1 Terminal-bench 43.3; Opus 4.5 Terminal-Bench 2.0 59.3.
- Opus 4 AI R&D-4 wording; Sonnet 4 Suite 1 (no numbers); Sonnet 4.5 AI R&D-4 wording; Sonnet 4.6 determination; Claude 3 Opus "no evals" row.

## Open questions / numbers not confirmed

1. **Claude 3.7 Sonnet Internal AI research evaluation suite** per-task results (kernel, time-series, text-based RL, LLM training) - card has them; not surfaced. Also exact subset size for the 70.3% custom-scaffold SWE-bench figure.
2. **Claude 4 (Opus 4 / Sonnet 4) Internal AI Research Evaluation Suite 2** score and any internal-use survey; Sonnet 4 per-task Suite 1 numbers.
3. **Opus 4.1** kernel-optimization speedup (card says slightly below Opus 4's 72.65x); whether the novel-compiler 74.4% / 6.81% figures are truly identical to Opus 4 or carried over in the snippet.
4. **Sonnet 4.5** Suite 2 score, other Suite 1 per-task numbers, and "Internal model evaluation and use survey" results.
5. **Opus 4.5** numeric Suite 1 values (kernel speedup, LLM-training speedup, quadruped, text-based RL); Terminal-Bench 2.0 59.3% is memory only.
6. **Opus 4.6** which Suite 1 task the 20.96 / 21.99 (threshold 12 = 4 human-effort hours) scores belong to (tentatively text-based RL); time-series / quadruped values; whether the card reports RE-Bench at all. Reconcile the "0 of 16" (Opus 4.7 card's summary of the 4.6 survey) vs "11 / 3 / 2 of 16" (Opus 4.6 card) framings.
7. **Sonnet 4.6** AI R&D section contents (likely "does not advance frontier beyond Opus 4.6"; no numbers found).
8. **Mythos Preview** exact card URL; Suite 2 numeric score if any (table is threshold-based); full survey counts; RE-Bench mention.
9. **Opus 4.7** survey counts (Zvi: "most not expecting a full drop-in L4; ~50/50 on weeklong ambiguous tasks"); Suite 1 numbers.
10. **Fable 5 / Mythos 5** card URL; survey counts; internal acceleration measure value; Terminal-Bench 2.1 for Mythos 5.
11. **Sonnet 5 SWE-bench Verified**: conflicting 72.7% (likely garbled - equals Sonnet 4's number) vs 85.2%. Left blank.
12. **Opus 5 SWE-bench Verified**: conflicting 96.0% (several secondary sites) vs "Anthropic did not report SWE-bench for Opus 5" (llm-stats, aireleasetracker). Left blank. Terminal-Bench 2.1 89.1% may be third-party rather than card-reported.
13. **Fable 5.1 / Mythos 5.1**: Anthropic reportedly published no SWE-bench Verified; survey / uplift numbers and Suite results not surfaced; METR tasks (Sunlight, Budget NanoGPT Speedrun, LMCA) only qualitative.
14. Whether any Anthropic card reports **PaperBench** (no evidence found) or a formal **AI R&D uplift RCT** (only surveys and the separate Jun 2026 "When AI builds itself" report: >80% of merged production code by Claude in May 2026; 130-staff poll median ~4x output with Mythos Preview; 8x code merged per engineer/day vs 2024, flagged by Anthropic as an overstatement).
15. Terminal-bench harness drift: Sonnet 4.5 announcement lists Opus 4.1 at 46.5% (Terminus 2) vs 43.3% at Opus 4.1 launch; benchmark versions move 1.0 -> 2.0 (Opus 4.5) -> 2.1 (Opus 4.8) -> 4.0 / -Science (Fable 5.1), so Terminal-bench rows are not directly comparable across cards.

---



# Chart-read values (2026-09-14)

The GPT-5.6 card (Figures 37 to 45) and the GPT-6 Astra card (Figures 52 to 55) report the Internal
Research Debugging Eval, KernelGen 1P, NanoGPT and PostTrainBench Lite only as curves of score against
API cost, simulated latency or output tokens. `scripts/digitize_curves.py` digitised every marker on
those charts into `data/ai_rd_scaling_curves.csv` (167 points; card page crops rendered at 260 dpi,
the Astra card's embedded PNGs). Check against printed values: Astra research debugging 78.1 read vs
78.05 printed; GPT-5.5 research debugging 49.9 read vs 50.5 printed in its own card (the 5.6 card
re-ran it). Rows that previously said "curves only; roughly N%" now carry the highest point on the
model's curve as their score, with confidence `chart` (mark ≈, hollow markers): GPT-5.6 Sol research
debugging 68.3, KernelGen 61.1, NanoGPT 16.6 (Astra card curve; 9.7 in its own card), PostTrainBench
56.7; GPT-6 Astra KernelGen 66.7, NanoGPT 23.6, PostTrainBench 77.0. GPT-5.4 Thinking and GPT-5.5
appear on the GPT-5.6 card's charts as comparison curves for KernelGen, NanoGPT and PostTrainBench,
which their own cards do not report; those values were added as rows sourced to the GPT-5.6 card.

The same pass for the other labs (2026-09-14): DeepMind's RE-Bench per-task bar charts (Gemini 2.5 Pro
card Figure 4, 2.5 Deep Think card Figure 4, Gemini 3 Pro FSF report Figure 5) were digitised by
`scripts/digitize_bars.py` into `data/ai_rd_rebench_tasks.csv` (80 bars). Cross-card check: Gemini 2.5
Pro 45 min on Optimize a Kernel reads 1.81, 1.81, 1.82 across the three cards; the human 8-hour bar
1.65, 1.65, 1.66. The Deep Think card's human-normalized average stays unfilled: the printed 2.5 Pro
average (0.73) is neither the mean of its 45-minute bars (0.64) nor of its 2-hour bars (0.89), so the
cards' average is not a function of the per-task bars. Anthropic: the Fable 5.1 card's CoBench figure
(2.3.4.1.A, p37) prints its values as bar labels, Mythos 5 45.6%, Opus 5 59.6%, Mythos 5.1 57.6%; the
row that said 'values in figure only' now carries 57.6 and the two comparison values were added as
rows sourced to that card. The Claude 3.7 Sonnet card's Suite 1 figures (21 to 23) are histograms and
box plots whose headline numbers (single run above 7x; RE-Bench subset average 0.2386) are already in
the table.

# Capability index versus self-reported uplift (2026-09-15)

AECI per Claude model: the Fable 5.1 card's Figure 2.3.5.A (p39) prints Mythos 5 159.46, Opus 5 160.73
and Mythos 5.1 161.98 and anchors Claude 3.5 Sonnet at 130; the other dots were read off the chart by
`scripts/digitize_aeci.py`, calibrated on the 130 and 161.98 points (the read values of the printed
points come out at 159.66 and 160.71, so the reading error is about 0.2). Earlier cards give slightly
different AECI values for the same model (Opus 4.8 card: Opus 4.7 154.1, Opus 4.8 155.5, Mythos Preview
158.3) because each card refits the index; the Fable 5.1 figure is used as one consistent snapshot.
Public Epoch ECI (eci_scores.csv, fetched 2026-09-15) exists for eight of the twelve models; it is
higher than AECI by 1.65 on average (sd 1.12). Uplift: Sonnet 4.5 card 9.3.5 (six numeric estimates
100/40/30/20/20/15 percent, one qualitative; median 25 percent taken as 1.25x), Opus 4.5 card (n=18,
median 100 percent, mean 220 percent), Opus 4.6 card (n=16, mean 152 percent, median 100 percent,
range 30 to 700 percent), Mythos Preview card 2.3.6 (informal Slack poll, about 130 respondents,
geometric mean about 4x, relative to zero AI assistance). ECI-to-compute: pooled fit over 46 Epoch
models with compute estimates, ECI = -84 + 8.8 log10(FLOP), residual sd 11.6; with a linear time term
the compute slope is 4.5 to 4.6 per tenfold and the time term 11.5 per year.
