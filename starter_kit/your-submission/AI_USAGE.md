# AI usage disclosure

I used Codex/ChatGPT as a programming and research assistant. It helped me
inspect the starter files, draft the Python/Powershell reproducibility scripts,
locate a public FLORES mirror after the initial Hugging Face route returned
401, and structure the markdown. It also suggested candidate flaws in
`fertility.py`; I did **not** accept them as findings until I ran an isolating
experiment and recorded its output.

It was misleading in two concrete ways. First, it proposed a nonexistent
future `regex` package pin; pip rejected it, and I corrected the pin only after
checking the installer’s available versions. Second, “NFC normalization is
harmless” would have been an easy assumption from the 10-line sample. I checked
the real corpus instead and found NFC changes token totals, so the report calls
it a documented preprocessing decision rather than a harmless line.

I personally verified the formulas in `partB/capacity.py`, the all-tokens
interpretation of `reported_tok_s`, the tokenizer tables in `results.json`, and
the arithmetic in the decision memo. The product recommendation is my
reasoned proposal, not a claim that it has been experimentally validated.
