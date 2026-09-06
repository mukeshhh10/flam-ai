# Part A — tokenizer audit

## A1. Evaluation corpus

I replaced the two 10-line toys with four parallel FLORES-200 `devtest` files:
English (`eng_Latn`), Hindi (`hin_Deva`), Kannada (`kan_Knda`), and Tamil
(`tam_Taml`). Each has 1,012 line-aligned sentences (4,048 total language
sentences). The included files and their SHA-256 hashes are recorded in
`results.json`; `analyze.py` asserts equal line counts before computing a
parallel-sentence comparison. I retained all nonempty lines, decoded UTF-8,
and NFC-normalized strings; I did **not** lowercase, remove punctuation, or
normalize whitespace. The source mirror is AI4Bharat/CTQScorer,
`dataset/test/*_Latn/Deva/Knda/Taml.devtest`; it distributes FLORES devtest
files. FLORES-200 is a multilingual translation evaluation set whose source
content is broad, Wikipedia-derived web text—not product chat.

That distinction is material: these 1,012 sentences are enough to defeat the
10-line toy’s instability and hold semantics constant across languages, but do
not measure our real prompt-length distribution, code-switching, romanized
Indic input, spelling noise, user-generated text, or output language mix.
Token counts predict cost only after those traffic proportions and the deployed
model/tokenizer are known. It also cannot tell us whether a more token-efficient
tokenizer/model is equally useful or safe.

## A2. Audit of `fertility.py`

All commands below were run from the repository root with the pinned
dependencies listed in `requirements.txt`. Their raw machine output is in
`audit_v0_output.txt`.

### 1. `split(" ")` counts empty “words” — confirmed code bug

**Experiment.** On the exact supplied sample, the output records 99 English
tokens. With canonical whitespace words it has 78 words, so `99/78 = 1.2692`;
the v0 space-split count has 79 words, so `99/79 = 1.2532`. Hindi similarly has
459 tokens, 61 canonical words (`7.5246`) but 62 space-split fields (`7.4032`).
The command was:

```powershell
& $py your-submission/partA/audit_v0.py | Tee-Object your-submission/partA/audit_v0_output.txt
```

**Result.** The double spaces in one line of each supplied file make the
reported corpus-weighted fertility **1.25% too low for English** and **1.61%
too low for Hindi**. The delta proves the bug because token counts stay fixed
while an empty field is added to the denominator. Use `re.findall(r"\S+")`,
not a literal-space split.

### 2. Mean of line ratios is not the reported corpus ratio — confirmed aggregation error

**Experiment.** Holding the lowercased strings and v0 space denominator fixed,
the v0 macro mean versus the token/word totals was English `1.2652` vs `1.2532`
and Hindi `7.4485` vs `7.4032` (same command/output above).

**Result.** The macro mean weights a two-word sentence the same as a 20-word
sentence; the claimed corpus figure instead needs total tokens / total units.
Here that inflates the displayed values by **0.96% English** and **0.61% Hindi**.
This is small in the toy only by accident; the effect varies with sentence
length and token density, so it must not be called a stable corpus statistic.

### 3. Lowercasing changes the thing being costed — confirmed measurement mutation

**Experiment.** On the English sample, case-preserved strings encode to 96 GPT-2
tokens; v0 lowercased strings encode to 99. On Hindi it is 459 in either case.
The same output shows case-preserved English fertility `96/78 = 1.2308` versus
lowercased `99/78 = 1.2692`.

**Result.** Lowercasing raises English tokens **3.1%** here and lowers the
Hindi/English ratio from `7.5246/1.2308 = 6.11×` to `7.5246/1.2692 = 5.93×`
before the other v0 choices. It is not safe to call casing “noise” when serving
cost is for the original request. Preserve input unless the production path also
lowercases it.

### 4. “Tokens per whitespace word” is the wrong cross-language cost denominator — confirmed conceptual flaw

**Experiment.** On the aligned 1,012-sentence corpus, GPT-2's total-token
ratios to English are, by whitespace word: Hindi `7.827/1.235 = 6.34×`, Kannada
`22.824/1.235 = 18.48×`, Tamil `25.047/1.235 = 20.28×`; by parallel sentence:
Hindi `198.324/26.723 = 7.42×`, Kannada `363.108/26.723 = 13.59×`, Tamil
`415.189/26.723 = 15.54×`. Reproduce with:

```powershell
& $py your-submission/partA/analyze.py --out your-submission/partA/results.json
```

**Result.** The same semantic units reach the server once each, while languages
do not have comparable whitespace-word segmentation. The word denominator
understates Hindi’s paired-request multiplier by 15% and overstates Kannada and
Tamil by 36% and 31%, respectively. The code does exactly what its label says;
the label is not the question capacity planning needs answered.

### 5. Suspicious but not a bug: `random.seed(1337)`

**Experiment.** `rg -n "random" fertility.py` returns only the import and
`random.seed(1337)`; neither `read_lines`, `analyze`, nor `main` draws from the
RNG. Re-running the command above cannot change from this seed because the
execution path contains no random operation.

**Result.** It is unnecessary dead code, but it does not affect a single token,
denominator, or printed number. I would remove it for clarity, not claim it
caused the report’s result.

### Normalization note

NFC was not blindly waved through: the toy files have zero changed lines, but
the larger snapshot has 93 Hindi, 7 Kannada, and 2 Tamil lines whose code-point
form changes. GPT-2 token totals raw→NFC are Hindi 200,483→200,704; Kannada
367,504→367,465; Tamil 420,177→420,171. NFC is therefore a disclosed corpus
canonicalization choice, not the harmless item above.

## A3. Corrected comparison

`analyze.py` uses total tokens/total denominator (not a mean of line ratios),
preserves case and whitespace, disables tokenizer special tokens, and computes
both whitespace-word and Unicode grapheme-cluster denominators. It uses GPT-2
as the deliberately non-Indic baseline and XLM-RoBERTa base as an open,
multilingual tokenizer. The results below are exact from `results.json`.

| tokenizer | language | tokens | tok / word | tok / grapheme | tok / UTF-8 byte | tok / aligned sentence |
|---|---:|---:|---:|---:|---:|---:|
| GPT-2 | English | 27,044 | 1.235 | 0.205 | 0.205 | 26.723 |
| GPT-2 | Hindi | 200,704 | 7.827 | 2.334 | 0.595 | 198.324 |
| GPT-2 | Kannada | 367,465 | 22.824 | 4.062 | 0.979 | 363.108 |
| GPT-2 | Tamil | 420,171 | 25.047 | 4.213 | 0.997 | 415.189 |
| XLM-R | English | 30,661 | 1.400 | 0.232 | 0.232 | 30.298 |
| XLM-R | Hindi | 38,221 | 1.491 | 0.445 | 0.113 | 37.768 |
| XLM-R | Kannada | 41,459 | 2.575 | 0.458 | 0.110 | 40.968 |
| XLM-R | Tamil | 41,354 | 2.465 | 0.415 | 0.098 | 40.864 |

For routing/cost, the one number I would use is **expected input tokens per
request for the deployed tokenizer, stratified by language and request type**.
For this controlled experiment its unbiased proxy is **tokens per aligned
sentence**: every row represents one semantically matched request, so the
denominator holds workload constant. Grapheme and byte rates are useful
diagnostics (they explain representation), but neither holds customer work
constant. Whitespace words are especially unsuitable for the decision.

## A4. Recommendation memo (≤1 page)

**Headline.** On 1,012 aligned FLORES sentences, GPT-2 averages 26.7 English,
198.3 Hindi, 363.1 Kannada, and 415.2 Tamil tokens per same-content request.
XLM-R averages 30.3, 37.8, 41.0, and 40.9 respectively. Thus GPT-2’s
same-content multipliers are **7.42× Hindi, 13.59× Kannada, and 15.54× Tamil**;
the multilingual tokenizer makes them **1.25×, 1.35×, and 1.35×**.

**Recommendation.** Do not budget “6× for Indic” or route all Indic traffic on
that basis. If model quality permits, route these language cohorts to a serving
path whose tokenizer is multilingual/Indic-aware; the controlled token savings
are very large, especially for Kannada/Tamil. Validate end-to-end quality and
latency before any model/tokenizer swap—token efficiency alone is not a routing
authorization.

**Biggest caveat.** FLORES is translated general-domain text, not our product’s
casual, code-switched traffic. Its measured multipliers may be wrong for our
actual prompt and completion mix.

**Production guardrail.** Monitor the p50/p95/**mean input-token count per
request**, broken down by detected language, script, and route (with sampling
for language-ID errors). This is the direct cost driver and will expose domain
or language-mix mismatch immediately; compare its observed route ratio to the
offline aligned-sentence ratio before using the latter for capacity budgets.
