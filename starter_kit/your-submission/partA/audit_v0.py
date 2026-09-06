#!/usr/bin/env python3
"""Isolated A2 experiments: report the effect of each v0 choice."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
from analyze import counts, load_tokenizer, read, v0

ROOT = Path(__file__).resolve().parent
KIT = ROOT.parent.parent

def emit(label, value): print(f"{label}: {json.dumps(value, ensure_ascii=False, sort_keys=True)}")

def main():
    enc = load_tokenizer("gpt2")
    # Exact intern corpus; isolate duplicate-space and lower-case effects.
    for lang, filename in [("eng", "eng_sample.txt"), ("hin", "hin_sample.txt")]:
        p = KIT / "corpus_sample" / filename
        raw = read(p, normalize=False, lowercase=False)
        lower = read(p, normalize=False, lowercase=True)
        emit(f"sample_{lang}_v0", v0(raw, enc))
        emit(f"sample_{lang}_global_space_lower", counts(lower, enc, "space"))
        emit(f"sample_{lang}_global_unicode_case_preserved", counts(raw, enc, "unicode"))
        emit(f"sample_{lang}_nfc_changed_lines", sum(a != b for a,b in zip(raw, read(p, normalize=True))))
    # Macro versus corpus-weighted aggregation on the real parallel corpus.
    for lang, filename in {"eng":"eng_Latn.devtest", "hin":"hin_Deva.devtest", "kan":"kan_Knda.devtest", "tam":"tam_Taml.devtest"}.items():
        lines = read(ROOT / "corpus" / filename)
        emit(f"flores_{lang}_v0", v0(lines, enc))
        emit(f"flores_{lang}_global", counts(lines, enc, "unicode"))

if __name__ == "__main__": main()
