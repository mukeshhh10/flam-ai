#!/usr/bin/env python3
"""Reproduce Part B arithmetic directly from the provided log."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
rows = list(csv.DictReader((ROOT.parent.parent / "bench" / "bench_log.csv").open()))
for r in rows:
    for k in ("batch_size", "prompt_len", "gen_len", "num_requests", "preempted_seqs"):
        r[k] = int(r[k])
    for k in ("wall_clock_s", "reported_tok_s", "kv_cache_util"):
        r[k] = float(r[k])

# K and V, fp16, for each GQA KV head, layer and head dimension.
kv_bytes_per_token = 28 * 8 * 128 * 2 * 2
usable_gb = 24 * 0.92
weight_gb = 4.2 * 2
kv_pool_gb = usable_gb - weight_gb - 1.6
seq_gb = kv_bytes_per_token * 4096 / 1e9
max_seqs = kv_pool_gb / seq_gb
print(f"kv_bytes_per_token={kv_bytes_per_token}")
print(f"kv_pool_gb={kv_pool_gb:.3f}")
print(f"4096_token_sequence_gb={seq_gb:.6f}")
print(f"max_4096_token_sequences={max_seqs:.2f} (floor {int(max_seqs)})")
print()
print("long_context_rows")
for r in rows:
    if r["prompt_len"] == 3584:
        generated = r["num_requests"] * r["gen_len"]
        actual_goodput = generated / r["wall_clock_s"]
        inferred_goodput = r["reported_tok_s"] * r["gen_len"] / (r["prompt_len"] + r["gen_len"])
        print(
            f"batch={r['batch_size']:2d} reported={r['reported_tok_s']:7.1f} "
            f"goodput={actual_goodput:6.1f} inferred={inferred_goodput:6.1f} "
            f"preempted={r['preempted_seqs']:2d} kv_util={r['kv_cache_util']:.2f}"
        )
