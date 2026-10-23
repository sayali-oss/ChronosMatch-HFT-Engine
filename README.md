# 

# \# ChronosMatch-HFT-Engine

# 

# A prototype high-frequency trading engine demonstrating order generation,

# memory-mapped ring-buffer communication, limit-order matching, and

# performance benchmarking.

# 

# \## Features

# 

# \- \*\*Market Firehose:\*\* Generates simulated BUY and SELL orders.

# \- \*\*Ring Buffer:\*\* Stores fixed-size order records in memory using `mmap`.

# \- \*\*Matching Engine:\*\* Matches compatible BUY and SELL orders using

# &#x20; price-time priority.

# \- \*\*Unit Tests:\*\* Tests ring-buffer behavior and matching-engine logic.

# \- \*\*Benchmarks:\*\* Measures order-processing throughput and ring-buffer

# &#x20; operation latency.

# 

# \## Project Structure

# 

# ```text

# ChronosMatch-HFT-Engine/

# ├── firehose/

# │   ├── firehose.py

# │   └── order\_generator.py

# ├── tests/

# │   ├── test\_ring\_buffer.py

# │   └── test\_matching\_engine.py

# ├── mmap\_ring\_buffer.py

# ├── matching\_engine.py

# ├── benchmark.py

# ├── benchmark\_latency.py

# ├── BENCHMARK\_RESULTS.md

# └── README.md

# ```

# 

# \## Requirements

# 

# \- Python 3.10 or later

# \- pytest for running the tests

# 

# Install pytest if needed:

# 

# ```bash

# python -m pip install pytest

# ```

# 

# \## Run the Matching Engine

# 

# ```bash

# python matching\_engine.py

# ```

# 

# The example submits a SELL order and then a compatible BUY order.

# The engine executes a trade and retains any unfilled quantity.

# 

# \## Run the Ring Buffer

# 

# ```bash

# python mmap\_ring\_buffer.py

# ```

# 

# \## Run Unit Tests

# 

# ```bash

# python -m pytest tests/ -v

# ```

# 

# \## Run Benchmarks

# 

# ```bash

# python benchmark.py

# python benchmark\_latency.py

# ```

# 

# Refer to `BENCHMARK\_RESULTS.md` for recorded benchmark measurements.

# 

# \## Limitations

# 

# This is a prototype, not a production-ready trading system. The current

# ring buffer uses anonymous memory mapping within one process; it does not

# yet demonstrate communication between independent processes. Benchmark

# results depend on the machine and test conditions.

# 

# The matching engine uses Python lists and is intended for demonstrating

# matching logic, not for claiming production-grade HFT performance.



