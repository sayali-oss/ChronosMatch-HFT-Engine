
# ChronosMatch Benchmark Results

## Environment
- Language: Python
- Ring buffer: mmap-based, 32-byte records
- Test type: Single-process benchmark

## Throughput

| Orders | Elapsed Time | Throughput |
|---:|---:|---:|
| 100,000 | 0.2986 s | 334,896.97 orders/sec |
| 1,000,000 | 2.9961 s | 333,768.04 orders/sec |

## Latency

| Metric | Result |
|---|---:|
| Orders processed | 100,000 |
| Average | 1.722 µs |
| p50 | 1.700 µs |
| p95 | 1.800 µs |
| p99 | 2.900 µs |
| Maximum | 62.700 µs |

## Observations
- Both throughput benchmarks passed.
- All generated orders were consumed.
- Throughput remained broadly consistent at the larger workload.
- The maximum observed latency was higher than the p99 latency.
- Results measure Python-level ring-buffer operations, not matching-engine latency.
- The buffer currently uses anonymous mmap and is not yet a separate-process IPC implementation.

## Next Steps
- Repeat benchmarks to assess run-to-run variation.
- Profile the hot path before optimization.
- Integrate with the matching engine and benchmark end-to-end behavior.
