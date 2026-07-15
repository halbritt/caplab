# Doctrine packet assembler baseline

This record preserves the measure-first evidence used to set the BOOKS-1
latency gate. It is an observation of one host on 2026-07-15, not a general
performance claim.

The request was:

```bash
python3 doctrine/tools/assemble_packet.py \
  --role coding-agent \
  --task implementation \
  --question 'Should this packet introduce a new interface?' \
  --signal 'public API' \
  --language Go \
  --risk correctness \
  --render json
```

The first observed call took 543.191 ms. After five warmups, 25 calls had a
560.174 ms median and a 598.279 ms nearest-rank p95.

An instrumented invocation separated startup and the assembler stages:

| Stage | Observed time |
|---|---:|
| Process launch and uncategorized work | 36.481 ms |
| Python imports | 73.822 ms |
| `Corpus` construction and YAML loading | 354.628 ms |
| Packet assembly | 58.253 ms |
| Packet schema validation | 6.769 ms |

Question-term selection accounted for 54.302 ms inside packet assembly. It
made 1,192 complete-phrase regular-expression calls, of which 52.391 ms was
spent in the regular-expression matcher. That selection measurement is a
subset of packet assembly and must not be added to the stage total.

The stage timings came from temporary `perf_counter_ns` probes around the
existing Python boundaries. The probes were removed after measurement; the
Python assembler was not changed. The repeatable acceptance harness is
[`benchmark_assemble_packet.py`](../../doctrine/tools/benchmark_assemble_packet.py),
and the final same-run comparison is
[`doctrine-packet-assembler-2026-07-15.json`](doctrine-packet-assembler-2026-07-15.json).

The delegated BOOKS-1 decision set these same-host acceptance thresholds:

- five warmup pairs and 25 measured pairs;
- candidate median no greater than 50 ms;
- candidate nearest-rank p95 no greater than 75 ms;
- median speedup of at least 8 times;
- semantic equality after removing only `retriever_version`,
  `packet_content_sha256`, and `packet_id`, with both packet identities
  independently recomputed.
