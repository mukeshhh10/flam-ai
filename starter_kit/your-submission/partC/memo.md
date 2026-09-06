# Decision memo — make Indic replies conversational

**Recommendation: (c) prompt-engineering only for this launch, with a
measurement gate; do not train or deploy a rewriter in the three-week window.**
Use an explicit locale/style system prompt plus 2–3 native, casual exemplars per
language and register-specific negative instructions (“avoid textbook/formal
honorific constructions unless the user uses them”). The model can be updated
or rolled back instantly, requires no new serving path, and leaves the A100 for
evaluation and contingency work. I would stage it by language rather than claim
that Hindi/Kannada validation transfers to Tamil, Telugu, Bengali, or Marathi.

**Assumptions.** We can generate a 600-prompt, six-language evaluation set from
realistic assistant tasks (100/language) without external APIs; each prompt has
one current and one candidate response. The reviewer can judge about 30 paired
responses/hour when allowed to flag fluency and register separately. Hindi and
Kannada are the only languages with reliable human labels; the other four get
automated regression checks and clearly labelled as unvalidated. The main model
already serves all six languages adequately enough that this is a style problem,
not a translation rescue.

**Back-of-envelope arithmetic.** A 100-prompt/language A/B set makes 1,200
responses. At 30 paired judgments/hour, 10 h/week gives 300 pairs/week, so the
reviewer can fully score **Hindi+Kannada: 200 pairs = 6.7 h** in week 1 and
reserve 3.3 h for adjudication; they cannot validate all six in time. Prompt
experiments cost approximately 1,200 model generations, no incremental GPU or
external-API spend. By contrast, a synthetic SFT needs a trusted seed/eval set
and a safety/regression loop before it has evidence of quality; the 2-week A100
budget is 336 A100-hours, but reviewer throughput—not training compute—is the
bottleneck. A ≤1B rewriter adds a second autoregressive pass to every reply;
even a modest 30-token rewrite adds roughly 30 output-token decode steps and a
new failure surface, with no reviewer capacity to tune it across six languages.

**Success metric.** On blinded paired judgments, the candidate wins on
“sounds naturally casual/conversational for this situation” in **≥65%** of
Hindi and Kannada pairs (two-sided binomial 95% CI lower bound >50%), while
fewer than **5%** of candidate answers receive a meaning/safety regression
flag. Report the six languages separately; do not average an unreviewed language
into the launch score.

**Kill criterion.** Abandon prompt-only for this launch if, by the end of day
5, either Hindi or Kannada has fewer than 55% candidate wins or >5% semantic/
safety regressions after one prompt revision. Then ship the current behavior and
use the remaining A100 time to collect a reviewed Hindi/Kannada seed set for a
post-launch SFT experiment; do not rush a synthetic SFT or rewriter into review.

**Day 1 experiment.** Freeze 100 Hindi and 100 Kannada prompts spanning support,
planning, explanation, and friendly chat. Produce baseline and a single
locale-style prompt candidate in randomized, blinded order. Have the reviewer
score 30 pairs/language for register, meaning preservation, and safety. This
reveals whether prompting has signal before spending a week generating synthetic
data or building a second serving path.
