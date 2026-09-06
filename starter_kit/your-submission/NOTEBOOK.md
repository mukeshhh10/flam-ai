# Lab notebook

All times are local (Asia/Kolkata). This is chronological; commands that
generated durable outputs are kept with the outputs rather than retyped.

## 2026-09-01 12:15 — intake

**Hypothesis.** The report may have mixed a tokenizer problem with a metric
problem, and the serving counter may not mean generated-token throughput.

**Experiment.** Read `fertility.py`, `REPORT_v0.md`, `bench/model_spec.md`, and
`bench/bench_log.csv` without changing them.

**Result/surprise.** The long-prompt row’s `reported_tok_s` exactly looked like
all requested tokens / wall time, not decode rate. `fertility.py` visibly
uses `split(" ")` and macro-averages ratios, but I treated neither as a claimed
flaw until measured.

## 2026-09-01 12:25 — reproducibility setup (dead end)

**Hypothesis.** Existing Python had `tiktoken` and Hugging Face tokenizer
support.

**Experiment.** Checked module availability with the bundled Python.

**Result/revision.** Neither was present. I installed pinned local dependencies
into `partA/vendor`. My first `regex==2026.8.8` pin did not exist on PyPI;
pip rejected it. I corrected it to the available `regex==2025.11.3` and
recorded the final pins in `partA/requirements.txt`. This is why I do not claim
the first install command as a successful experiment.

## 2026-09-01 12:40 — corpus acquisition (dead end and revision)

**Hypothesis.** FLORES+ could be fetched directly from its Hugging Face
endpoint.

**Experiment.** Tried the public `openlanguagedata/flores_plus` resolve URL and
the Hugging Face dataset-server rows API.

**Result/revision.** Both returned HTTP 401 in this environment. I did not
substitute generated translations. Web search located AI4Bharat/CTQScorer’s
public mirror of the FLORES devtest files; I downloaded English/Hindi/Kannada/
Tamil, checked each has 1,012 lines, and pinned their SHA-256 in
`partA/fetch_corpus.ps1` and `results.json`.

## 2026-09-01 13:05 — baseline audit

**Hypothesis.** The supplied samples’ double spaces and lowercasing measurably
distort the published 5.89× figure.

**Experiment.** Ran `partA/audit_v0.py`; raw output is
`partA/audit_v0_output.txt`.

**Result/revision.** Literal-space splitting creates one empty denominator unit
in each sample and lowers fertility by 1.25% English / 1.61% Hindi on
corpus-weighted totals. Lowercasing adds three GPT-2 English tokens (96→99),
while Hindi is unchanged. Macro aggregation also differs from totals. These are
now claims in `partA/analysis.md` with their exact deltas, rather than just
code-review observations.

## 2026-09-01 13:25 — a suspicious line that was *not* blamed

**Hypothesis.** `random.seed(1337)` might hide sampling behavior.

**Experiment.** Searched every use of `random` in `fertility.py`.

**Result.** Only the import and seed exist; no sampled operation reaches the
analysis. It is dead code, not a numerical bug. Separately, I checked NFC:
unlike the toy corpus, it changes 93 Hindi, 7 Kannada, and 2 Tamil FLORES
strings and can alter GPT-2 totals, so I disclosed it as preprocessing rather
than calling it harmless.

## 2026-09-01 13:40 — corrected tokenizer comparison

**Hypothesis.** Same-content sentence token counts will change the routing
conclusion more than “tok/word.”

**Experiment.** Ran `partA/analyze.py` using GPT-2 and XLM-R tokenizer vocabularies
with no special tokens, preserving case. Durable output: `partA/results.json`.

**Result.** GPT-2 uses 7.42×/13.59×/15.54× English tokens per same translated
sentence for Hindi/Kannada/Tamil; XLM-R reduces those to 1.25×/1.35×/1.35×.
The word-rate ratios disagree materially, confirming the denominator is the
decision error, not merely a presentation preference.

## 2026-09-01 14:05 — capacity check

**Hypothesis.** KV memory admits roughly 24–25 full 4096-token sequences and
the long-batch collapse is preemption.

**Experiment.** Ran `partB/capacity.py`; output saved in
`partB/capacity_output.txt`.

**Result.** The arithmetic predicts 25.72 sequences; batch 24 is at 0.93 KV
utilization with no preemptions, batch 32/48 hit 0.97 with 7/23 preemptions.
The log’s 1,607.4 is exactly all requested (prompt+generated) tokens / seconds;
actual batch-24 generated goodput is 200.9 tok/s. I revised the recommendation
to cap at 24 and queue excess work, with a labelled predicted 24% 48-request
goodput improvement.

## 2026-09-01 14:25 — product decision

**Hypothesis.** Reviewer throughput, not A100 hours, constrains a trustworthy
six-language style launch.

**Experiment.** Budgeted 600 prompts and 30 paired judgments/hour against the
10 h/week Hindi/Kannada-only reviewer constraint.

**Result.** A prompt-only A/B can be judged in Hindi/Kannada during week one;
neither synthetic SFT nor a rewriter can be validated across all languages by
review. Wrote the gated, reversible prompt recommendation in `partC/memo.md`.
