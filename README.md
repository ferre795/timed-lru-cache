# TimedLRUCache (Python)

An O(1) LRU cache with TTL expiration and thread safety.

## Features
- O(1) get/set via dict + doubly linked list
- Time-to-live (TTL) expiration
- Thread-safe (`threading.Lock`)
- Basic stats: hits, misses, removals, expirations

## Quick Start
```bash
python bench_single.py
python bench_multi.py
