# Part B — capacity reconciliation

Commands and output are in `capacity.py` / `capacity_output.txt`:

```powershell
py -3 your-submission/partB/capacity.py | Tee-Object your-submission/partB/capacity_output.txt
```

## B1 — KV capacity

Each token stores K and V for every layer and each GQA KV head, in fp16:

`28 layers × 8 KV heads × 128 head_dim × 2 (K,V) × 2 bytes = 114,688 bytes/token`

That is 112 KiB/token. The memory budget using the spec's decimal-GB quantities is
`24 × .92 − 4.2B × 2 bytes − 1.6 = 12.08 GB` for KV. A full 4096-token
sequence consumes `114,688 × 4096 = 469,762,048 bytes = 0.4698 GB`.
Therefore `12.08 / 0.4698 = 25.72`, or about **25 concurrent full-context
sequences** (not 48). The log corroborates the boundary: at long-context batch
24, KV utilization is 0.93 with zero preemptions; batch 32 reaches 0.97 and
preempts 7 sequences. The small gap from 25 to 24 is expected from block
rounding/allocator headroom and the deliberately approximate 1.6 GB overhead.

## B2 — long-context anomaly

The apparent throughput peak is batch 24 (1,607.4 reported tok/s), then it
*falls* to 1,384.0 at batch 32 and 1,298.5 at batch 48. This is not ordinary
batch scaling: `preempted_seqs` jumps 0 → 7 → 23 and `kv_cache_util` saturates
0.93 → 0.97 → 0.97. KV blocks are exhausted; the scheduler preempts/recomputes
or swaps sequences, so extra requests increase contention rather than useful
decode work. TTFT confirms it (500.5 ms at 24, 636.9 at 32, 955.4 at 48).

Set the admission/concurrency cap (`max_num_seqs`) to **24** on this L4 and
queue excess requests. For 48 simultaneous requests, two 24-request waves are
predicted to take `2 × 61.16 = 122.32 s`, yielding `24,576 / 122.32 = 200.9`
generated tok/s instead of the observed `24,576 / 151.41 = 162.3`: about a
**24% goodput increase**, while eliminating the preemption regime. A second L4
with 24 requests each would instead target about 402 generated tok/s.

## B3 — the misleading column

`reported_tok_s` counts **input plus generated tokens divided by wall time**,
not output-token serving throughput. For example, the batch-24 long row is
`24 × (3584 + 512) / 61.16 = 1,607.4`, exactly the reported value. Longer
prompts therefore inflate this counter before any capacity improvement, and
linear extrapolation to batch 48 ignores the preemption rows.

The honest batch-24 output goodput is **200.9 generated tok/s**, shown two
independent ways: (1) `24 × 512 / 61.16 = 200.9`; (2)
`1,607.4 × 512 / (3584 + 512) = 200.9`. The report should have said: “At a
safe long-context concurrency of 24, this L4 completed about 201 output tok/s;
the 1,607 counter includes prompt tokens. At higher concurrency, KV pressure
reduces rather than increases goodput.”

## B4 — confirmation counter

Pull the serving engine's **KV-cache preemption counter** (for example,
vLLM's cumulative preemption metric) per replica. Under a capped-24 long
context load I expect **0 preemptions** over the measurement interval; under
the batch-32/48 pattern it should be nonzero and rise with offered concurrency,
as the log's 7 and 23 rows already suggest. That direct transition tests the
mechanism, unlike GPU utilization, which can remain high in both productive and
thrashing states.
