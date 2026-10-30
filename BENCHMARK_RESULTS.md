
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

## 6. Historical Test Results

- Original unit and integration test suite: 24 passed.
- Later regression suite: 26 passed.
- Firehose integration: PASS.
- Matching-engine benchmark: PASS.
- Million-order pipeline benchmark: PASS.

These results are retained as historical records from their respective benchmark stages.

## 7. Day 13 — Repeated Matching Engine Benchmark

### Benchmark Configuration

| Setting | Result |
|---|---|
| Orders per run | 10,000 |
| Repetitions | 5 |
| Random seed | 42 |
| Benchmark result | PASS |
| Outcome consistency | PASS |
| Regression tests | 26 passed |

### Throughput Results

| Run | Throughput | Average Latency |
|---:|---:|---:|
| 1 | 317,582.31 orders/sec | 3.015 µs |
| 2 | 282,961.47 orders/sec | 3.348 µs |
| 3 | 301,587.25 orders/sec | 3.180 µs |
| 4 | 256,038.02 orders/sec | 3.748 µs |
| 5 | 315,326.11 orders/sec | 3.039 µs |
| **Median** | **301,587.25 orders/sec** | **3.180 µs** |

### Final-Run Latency and Order-Book Results

| Metric | Result |
|---|---:|
| Elapsed time | 0.0317 s |
| p50 latency | 2.500 µs |
| p95 latency | 5.100 µs |
| p99 latency | 8.100 µs |
| Maximum latency | 1,116.900 µs |
| Trades executed | 7,753 |
| Open BUY orders | 1,096 |
| Open SELL orders | 1,144 |
| Status | PASS |

### Observations

- Median throughput across five runs was 301,587.25 orders/sec.
- Median average latency across the five runs was 3.180 µs.
- Run-to-run throughput varied from 256,038.02 to 317,582.31 orders/sec.
- The final run's maximum latency was substantially higher than its p99 latency, indicating a tail-latency outlier worth investigating.
- Outcome consistency passed for the benchmark workload.
- The regression suite passed with 26 tests.
- These measurements represent the matching-engine benchmark, not end-to-end latency across the firehose, ring buffer, and matching engine.
- Results depend on hardware, operating-system activity, workload, and benchmark methodology. They do not establish production-grade HFT performance.

## 8. Day 15 — Matching Engine Object-Creation Optimization

### Objective

Reduce unnecessary object-initialization overhead when processing standard orders.

### Optimization Applied

The `_Order.__init__()` method was modified to include a fast path for standard orders.

Standard firehose orders contain exactly five required fields:

- order_id
- side
- price
- quantity
- timestamp

Previously, every order created a reserved-field set and iterated through the order dictionary to identify additional fields.

The optimized implementation checks the dictionary length first:

```python
if len(order) == 5:
    self.extra_fields = None
else:
    reserved = {
        "order_id",
        "side",
        "price",
        "quantity",
        "timestamp",
        "remaining",
        "sequence",
    }

    extras = {
        key: value
        for key, value in order.items()
        if key not in reserved
    }
    self.extra_fields = extras or None
```

This avoids unnecessary set creation and dictionary iteration for standard five-field orders.

Orders containing additional custom fields continue to use the original extra-field handling logic.

### Benchmark Configuration

| Setting | Result |
|---|---|
| Orders per run | 10,000 |
| Repetitions per session | 5 |
| Random seed | 42 |
| Baseline sessions | 1 |
| Post-optimization sessions | 3 |
| Matching-engine implementation | Python |
| Benchmark type | Matching-engine-only |
| Outcome consistency | PASS |

### Baseline Results

The baseline was recorded immediately before applying the optimization.

| Metric | Result |
|---|---:|
| Median throughput | 327,829.08 orders/sec |
| Median average latency | 2.935 µs |
| Final-run elapsed time | 0.0308 s |
| Final-run p50 latency | 2.400 µs |
| Final-run p95 latency | 5.100 µs |
| Final-run p99 latency | 8.300 µs |
| Final-run maximum latency | 441.800 µs |
| Trades executed | 7,753 |
| Open BUY orders | 1,096 |
| Open SELL orders | 1,144 |
| Status | PASS |

### Post-Optimization Throughput Results

Three independent benchmark sessions were executed after the optimization.

**Session 1**

| Run | Throughput | Average Latency |
|---:|---:|---:|
| 1 | 334,206.73 orders/sec | 2.815 µs |
| 2 | 378,522.63 orders/sec | 2.530 µs |
| 3 | 385,120.48 orders/sec | 2.470 µs |
| 4 | 382,210.40 orders/sec | 2.482 µs |
| 5 | 317,012.47 orders/sec | 2.940 µs |
| **Median** | **378,522.63 orders/sec** | **2.530 µs** |

**Session 2**

| Run | Throughput | Average Latency |
|---:|---:|---:|
| 1 | 334,784.06 orders/sec | 2.832 µs |
| 2 | 373,028.54 orders/sec | 2.557 µs |
| 3 | 372,062.57 orders/sec | 2.559 µs |
| 4 | 395,900.06 orders/sec | 2.413 µs |
| 5 | 375,668.69 orders/sec | 2.548 µs |
| **Median** | **373,028.54 orders/sec** | **2.557 µs** |

**Session 3**

| Run | Throughput | Average Latency |
|---:|---:|---:|
| 1 | 321,931.59 orders/sec | 2.952 µs |
| 2 | 400,735.75 orders/sec | 2.391 µs |
| 3 | 363,726.30 orders/sec | 2.609 µs |
| 4 | 404,855.02 orders/sec | 2.372 µs |
| 5 | 374,936.26 orders/sec | 2.540 µs |
| **Median** | **374,936.26 orders/sec** | **2.540 µs** |

### Consolidated Performance Comparison

| Metric | Baseline | Post-Optimization |
|---|---:|---:|
| Median throughput | 327,829.08 orders/sec | 375,495.81 orders/sec* |
| Median average latency | 2.935 µs | 2.540 µs* |

*Post-optimization figures are the arithmetic means of the three independent session medians.

### Performance Improvement

| Measurement | Change |
|---|---:|
| Throughput improvement | Approximately 14.54% |
| Average latency reduction | Approximately 13.45% |

The throughput improvement is calculated by comparing the mean of the three post-optimization session medians against the baseline session median.

### Latest Session Latency Results

| Metric | Baseline | Latest post-optimization session |
|---|---:|---:|
| p50 | 2.400 µs | 2.200 µs |
| p95 | 5.100 µs | 4.600 µs |
| p99 | 8.300 µs | 7.000 µs |
| Maximum | 441.800 µs | 393.000 µs |

These percentile and maximum measurements are from the final run of each respective benchmark session.

### Correctness Verification

| Check | Result |
|---|---|
| Unit and integration tests | 26 passed |
| Trades executed | 7,753 |
| Open BUY orders | 1,096 |
| Open SELL orders | 1,144 |
| Outcome consistency | PASS |
| Custom order field preservation | PASS |
| Benchmark result | PASS |

A custom-field check confirmed that an additional `symbol` field remains present in the public order-book snapshot.

### Observations

- The fast path reduced unnecessary dictionary processing for standard orders.
- All three post-optimization benchmark sessions produced higher median throughput than the baseline.
- The average of the three post-optimization session medians was approximately 14.54% above the baseline.
- Matching outcomes remained consistent across all benchmark sessions.
- The P50, P95, and P99 latency measurements in the latest session were lower than the baseline measurements.
- Benchmark timing still varies between runs, so the results should be interpreted in the context of the test environment.
- The optimization improves the measured Python matching-engine workload; it does not establish end-to-end HFT latency or production-grade performance.

## 9. Observations and Limitations

- Heap-based price-time order-book management substantially improved the measured matching-engine performance.
- The Day 15 object-initialization fast path further improved measured matching-engine throughput.
- The ring buffer uses anonymous mmap and has not been verified as an independent-process IPC implementation.
- The matching engine is currently implemented in Python, not Cython.
- The under-50-microsecond end-to-end target has not yet been established by these benchmarks.
- Maximum observed matching-engine latency can be substantially higher than average and percentile measurements.
- Results depend on hardware, operating system, workload, and benchmark conditions.
- These measurements do not establish production-grade high-frequency trading performance.

## 10. Next Steps

1. Run additional benchmark sessions to monitor performance variation.
2. Profile the matching engine using a representative workload.
3. Investigate further optimization opportunities based on profiling evidence.
4. Verify the remaining project requirements, including Cython ownership and implementation.
5. Confirm whether the ring buffer needs independent-process IPC.
6. Measure end-to-end latency across order generation, ring-buffer transport, and matching.
