#!/usr/bin/env python3
"""Reproducible tokenizer audit for the included FLORES-200 devtest snapshot."""
import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENDOR = ROOT / "vendor"
sys.path.insert(0, str(VENDOR))
import regex  # noqa: E402

LANGS = {"eng": "eng_Latn.devtest", "hin": "hin_Deva.devtest",
         "kan": "kan_Knda.devtest", "tam": "tam_Taml.devtest"}


def load_tokenizer(name):
    if name == "gpt2":
        import tiktoken
        return lambda s: tiktoken.get_encoding("gpt2").encode(s)
    if name == "xlmr":
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained("xlm-roberta-base")
        return lambda s: tok.encode(s, add_special_tokens=False)
    raise ValueError(name)


def read(path, normalize=True, lowercase=False):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines:
        if normalize:
            line = unicodedata.normalize("NFC", line)
        if lowercase:
            line = line.lower()
        if line:
            out.append(line)
    return out


def counts(lines, encode, word_mode="unicode"):
    tokens = sum(len(encode(x)) for x in lines)
    if word_mode == "space":
        words = sum(len(x.split(" ")) for x in lines)  # v0 behavior
    else:
        words = sum(len(re.findall(r"\S+", x, flags=re.UNICODE)) for x in lines)
    chars = sum(len(x) for x in lines)
    graphemes = sum(len(regex.findall(r"\X", x)) for x in lines)
    utf8_bytes = sum(len(x.encode("utf-8")) for x in lines)
    return {"sentences": len(lines), "tokens": tokens, "words": words,
            "codepoints": chars, "graphemes": graphemes, "utf8_bytes": utf8_bytes,
            "tok_per_word": tokens / words, "tok_per_grapheme": tokens / graphemes,
            "tok_per_utf8_byte": tokens / utf8_bytes, "tok_per_sentence": tokens / len(lines)}


def v0(lines, encode):
    fert = [len(encode(x.lower())) / len(x.lower().split(" ")) for x in lines]
    tpc = [len(encode(x.lower())) / len(x.lower()) for x in lines]
    return {"macro_tok_per_space_word": sum(fert) / len(fert),
            "macro_tok_per_codepoint": sum(tpc) / len(tpc)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(ROOT / "corpus"))
    ap.add_argument("--out", default=str(ROOT / "results.json"))
    ap.add_argument("--tokenizer", action="append", choices=["gpt2", "xlmr"], default=[])
    args = ap.parse_args()
    names = args.tokenizer or ["gpt2", "xlmr"]
    corpus = Path(args.corpus)
    result = {"corpus": {}, "tokenizers": {}}
    all_lines = {}
    for lang, filename in LANGS.items():
        path = corpus / filename
        raw = path.read_bytes()
        lines = read(path)
        all_lines[lang] = lines
        result["corpus"][lang] = {"file": filename, "sha256": hashlib.sha256(raw).hexdigest(), "sentences": len(lines)}
    assert len({len(x) for x in all_lines.values()}) == 1, "parallel sentence counts differ"
    for name in names:
        encode = load_tokenizer(name)
        result["tokenizers"][name] = {lang: {"corrected": counts(lines, encode), "v0": v0(lines, encode)} for lang, lines in all_lines.items()}
    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
