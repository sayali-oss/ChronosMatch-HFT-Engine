
# ChronosMatch Benchmark Results

## Environment

- Language: Python
- Ring buffer: mmap-based, 32-byte records
- Matching engine: Heap-based limit order book
- Test type: Single-process benchmark
- Order priority: Price-time priority

## 1. Ring Buffer Throughput

| Orders | Elapsed Time | Throughput | Status |
|---:|---:|---:|---|
| 100,000 | 0.2986 s | 334,896.97 orders/sec | PASS |
| 1,000,000 | 2.9961 s | 333,768.04 orders/sec | PASS |

These results measure the ring-buffer pipeline. They do not represent matching-engine throughput.

## 2. Ring Buffer Latency

| Metric | Result |
|---|---:|
| Orders processed | 100,000 |
| Average | 1.722 µs |
| p50 | 1.700 µs |
| p95 | 1.800 µs |
| p99 | 2.900 µs |
| Maximum | 62.700 µs |

These are the previously recorded measurements from the ring-buffer latency benchmark.

## 3. Matching Engine Performance

### Before heap optimization

| Metric | Result |
|---|---:|
| Orders processed | 10,000 |
| Elapsed time | 2.5035 s |
| Throughput | 3,994.46 orders/sec |
| Average latency | 250.346 µs |
| p50 latency | 225.000 µs |
| p95 latency | 516.400 µs |
| p99 latency | 802.600 µs |
| Maximum latency | 5,233.700 µs |
| Trades executed | 7,679 |
| Open BUY orders | 1,151 |
| Open SELL orders | 1,163 |
| Status | PASS |

### After heap optimization

| Metric | Result |
|---|---:|
| Orders processed | 10,000 |
| Elapsed time | 0.0445 s |
| Throughput | 224,575.78 orders/sec |
| Average latency | 4.453 µs |
| p50 latency | 3.300 µs |
| p95 latency | 7.500 µs |
| p99 latency | 10.800 µs |
| Maximum latency | 2,457.000 µs |
| Trades executed | 7,799 |
| Open BUY orders | 1,031 |
| Open SELL orders | 1,165 |
| Status | PASS |

The heap-based implementation avoids repeatedly sorting the entire order book after every order. In these two runs, measured matching-engine throughput increased substantially and average latency decreased.

These figures are single-run measurements and should be validated across repeated runs. The benchmark measures the Python `add_order()` operation, including matching and order-book maintenance.

## 4. Firehose Integration

| Metric | Result |
|---|---:|
| Orders generated | 5,000 |
| Orders consumed | 5,000 |
| Record size | 32 bytes |
| Time taken | 0.099702 s |
| Throughput | 50,149.29 orders/sec |
| Trades executed | 3,827 |
| Open BUY orders | 591 |
| Open SELL orders | 579 |
| Status | PASS |

The firehose integration successfully generated and consumed all 5,000 orders with the optimized matching engine.

## 5. Million-Order Pipeline Benchmark

| Metric | Result |
|---|---:|
| Orders generated | 1,000,000 |
| Orders consumed | 1,000,000 |
| Elapsed time | 6.7335 s |
| Throughput | 148,511.02 orders/sec |
| Status | PASS |

This benchmark measures the existing million-order pipeline, not the matching engine in isolation.

The earlier recorded million-order throughput was 150,876.22 orders/sec. The latest run is broadly comparable, and run-to-run variation should be evaluated through repeated measurements.

## 6. Test Results

- Unit and integration test suite: 24 passed.
- Firehose integration: PASS.
- Matching-engine benchmark: PASS.
- Million-order pipeline benchmark: PASS.
- Git changes committed and pushed to `teammate1-dev`.

## 7. Observations and Limitations

- Heap-based price-time order-book management substantially improved the measured matching-engine performance.
- The ring buffer uses anonymous mmap and has not been verified as an independent-process IPC implementation.
- The matching engine is currently implemented in Python, not Cython.
- The under-50-microsecond end-to-end target has not yet been established by these benchmarks.
- The maximum observed matching-engine latency was 2,457 µs, despite much lower average and percentile measurements.
- Results depend on the hardware, operating system, workload, and benchmark conditions.
- These measurements do not establish production-grade high-frequency trading performance.

## 8. Next Steps

1. Repeat matching-engine and ring-buffer benchmarks to measure run-to-run variation.
2. Profile the matching engine using a representative workload.
3. Verify the remaining project requirements, including Cython ownership and implementation.
4. Confirm whether the ring buffer needs independent-process IPC.
5. Measure end-to-end latency across order generation, ring-buffer transport, and matching.
