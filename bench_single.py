import time
import random
from TimedLRUCache import TimedLRUCache 

def bench_single(
    capacity=1000,
    ttl=5.0,
    duration=3.0,
    n_keys=10_000,
    read_ratio=0.90,
    log_interval_ops = 100000, 
):
    cache = TimedLRUCache(capacity=capacity, ttl=ttl)

    # Preload exactly 'capacity' unique keys so we start full.
    for k in range(capacity):
        cache.set(k, 0)

    # Snapshot stats before the timed run so we can subtract them out later.
    pre = cache.stats()

    start = time.perf_counter()
    ops = gets = sets = 0
    end = start + duration
    while time.perf_counter() < end:
        if random.random() < read_ratio:
            cache.get(random.randrange(n_keys))
            gets += 1
        else:
            k = random.randrange(n_keys)
            cache.set(k, k)
            sets += 1
        ops += 1

        if ops % log_interval_ops == 0:
            stats = cache.stats()
            hits = stats.get("hits", 0)
            misses = stats.get("misses", 0)
            denom = max(1, hits + misses)
            hit_rate = hits / denom
            print(f"[{ops:,} ops] Hit rate: {hit_rate*100:.2f}%")
    
    wall = time.perf_counter() - start

    post = cache.stats()
    hits = post["hits"] - pre["hits"]
    misses = post["misses"] - pre["misses"]
    evictions = (post.get("evictions", post.get("removals", 0))
                 - pre.get("evictions", pre.get("removals", 0)))
    expirations = post["expirations"] - pre["expirations"]
    run_hit_rate = hits / max(1, (hits + misses))

    print("TimedLRUCache Benchmark (single-thread)")
    print(f"  Capacity: {capacity}, TTL: {ttl}s, Working set: {n_keys}, Read ratio: {int(read_ratio*100)}%")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Ops: {ops:,}  (gets: {gets:,}, sets: {sets:,})")
    print(f"  Throughput: {int(ops/wall):,} ops/sec")
    print(f"  Hit rate: {run_hit_rate*100:.2f}%  Evictions: {evictions}  Expirations: {expirations}")
    print(f"  Final stats: {post}")

if __name__ == "__main__":
    bench_single()
