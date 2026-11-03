
# ChronosMatch-HFT-Engine
Zero-Copy high-frequency Trading ENgine in python
# ChronosMatch-HFT-Engine

ChronosMatch is a zero-copy high-frequency trading engine built in Python.  
It simulates buy/sell orders, matches them in real time, and displays stats on a live dashboard.

---

## 🚀 Setup Instructions
1. Install Python 3.10+ and Git.
2. Clone the repository:
   ```bash
   git clone https://github.com/your-repo.git
   cd ChronosMatch-HFT-Engine
# to checkout your branch
git checkout teammateX-dev

# Daily Commit Routine

git pull origin teammateX-dev
git add .
git commit -m "Day X: what you did"
git push origin teammateX-dev

# Team Roles (Week 1)
Teammate 1 → Ring buffer (mmap + struct)

Teammate 2 → Async firehose (asyncio)

Teammate 3 → Order book skeleton

Teammate 4 → Dashboard skeleton (curses)

# Day-wise Plan (Week 1)
# Day 1 (Setup & Basics)

T1: Ring buffer demo

T2: Firehose generator

T3: Order book skeleton

T4: Dashboard skeleton

# Day 2 (Integration)

T1: Connect buffer to firehose

T2: Push orders into buffer

T3: Insert logic for buy/sell

T4: Show “Orders received” counter

# Day 3 (Testing Flow)

T1: Test buffer speed

T2: Stress test firehose

T3: Retrieval from order book

T4: Show buffer usage %

# Day 4 (Refinement)

T1: Circular overwrite logic

T2: Realistic price/quantity ranges

T3: Draft matching logic

T4: Latency placeholder

# Day 5 (Milestone Check)

Run full pipeline: firehose → buffer → order book → dashboard

Each teammate commits daily progress with clear messages

# ✅ Contribution Rules
Work only in your assigned branch.

Push daily commits with clear messages.

Weekly merge into main after review
Week 2 Progress Plan
Teammate 1 - Order Book (Cython)
Day 6
Setup Cython
Create orderbook.pyx
Design Buy Order structure
Day 7
Buy order insertion logic
Order storage testing
Day 8
Implement matching algorithm
Day 9
Optimize matching speed
Day 10
Finalize Cython implementation
Teammate 2 - Matching Engine
Day 6
Design Sell Order structure
Study Price-Time Priority
Day 7
Sell order insertion logic
Day 8
Partial fill handling
Trade execution logic
Day 9
Edge case handling
Day 10
Matching accuracy testing
Teammate 3 - Integration & Testing
Day 6
Connect Firehose with Order Book
Day 7
Test order insertion
Day 8
Validate matched trades
Day 9
Stress test with 10K+ orders
Day 10
Integration testing
Week 2 verification
Teammate 4 - Dashboard Monitoring
Day 6
Read data from engine.log
Day 7
Read data from engine.json
JSON parsing
Day 8
High Latency Alert
Buffer Overflow Alert
Day 9
Health Status System
NORMAL
WARNING
CRITICAL
Day 10
UI polishing
Dashboard cleanup
Final Week 2 Demo
Week 2 Deliverables
Working Cython Order Book
Matching Engine
Dashboard Alerts
JSON Integration
Real-time Monitoring Dashboard
