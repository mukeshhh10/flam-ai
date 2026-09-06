# Part A: reproducible tokenizer audit

Corpus: the 1,012 sentence, line-aligned FLORES-200 `devtest` files for English
(`eng_Latn`), Hindi (`hin_Deva`), Kannada (`kan_Knda`) and Tamil (`tam_Taml`).
They were copied from the `master` branch of AI4Bharat/CTQScorer on 2026-09-01;
the source repository contains the FLORES test files. `analyze.py` records the
SHA-256 of each included file and asserts alignment by line count. FLORES is
professionally translated, Wikipedia-derived general-domain evaluation text;
it is not a sample of our assistant traffic, informal chat, code-switching,
romanized Indic text, or user prompts. It estimates tokenizer representation
on aligned content, not product mix or completion length.

Run (portable reproduction):

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r your-submission/partA/requirements.txt
.\.venv\Scripts\python.exe your-submission/partA/analyze.py --out your-submission/partA/results.json
.\.venv\Scripts\python.exe your-submission/partA/audit_v0.py | Tee-Object your-submission/partA/audit_v0_output.txt
```

Dependencies are pinned in `requirements.txt`. `analyze.py` may use a local
`vendor/` directory if present, but does not require one. `gpt2` means OpenAI's GPT-2 BPE;
`xlmr` means `xlm-roberta-base` with special tokens disabled. The first run
downloads public tokenizer vocabulary files into the Hugging Face cache.
