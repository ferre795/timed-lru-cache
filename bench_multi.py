import time
import random
import threading
from TimedLRUCache import TimedLRUCache  

def worker(cache, n_keys, read_ratio, duration, result_dict, idx, result_lock):
    gets = sets = ops = 0
    end = time.perf_counter() + duration
    while time.perf_counter() < end:
        if random.random() < read_ratio:
            cache.get(random.randrange(n_keys))
            gets += 1
        else:
            k = random.randrange(n_keys)
            cache.set(k, k)
            sets += 1
        ops += 1
    with result_lock:
        result_dict[idx] = (ops, gets, sets)
    

def bench_multi(
    threads=8,
    capacity=1000,
    ttl=5.0,
    duration=3.0,
    n_keys=10_000,
    read_ratio=0.90,
):
    cache = TimedLRUCache(capacity=capacity, ttl=ttl)

    # Preload to capacity with unique keys
    for k in range(capacity):
        cache.set(k, 0)

    # Snapshot before run
    pre = cache.stats()

    # Launch workers
    results = {}
    result_lock = threading.Lock()
    ts = [threading.Thread(target=worker,
                           args=(cache, n_keys, read_ratio, duration, results, i, result_lock))
          for i in range(threads)]

    start = time.perf_counter()
    for t in ts: t.start()

    #Hit log every 1 second while workers are running
    next_log = start + 1.0
    end_time = start + duration
    while time.perf_counter() < end_time:
        if time.perf_counter() >= next_log:
            stats = cache.stats()
            hits = stats.get("hits", 0)
            misses = stats.get("misses", 0)
            denom = max(1, hits + misses)
            hit_rate = hits / denom
            print(f"Hit rate: {hit_rate*100:.2f}%")
            next_log += 1.0

    for t in ts: t.join()
    wall = time.perf_counter() - start  

    total_ops = sum(r[0] for r in results.values())
    total_gets = sum(r[1] for r in results.values())
    total_sets = sum(r[2] for r in results.values())

    post = cache.stats()
    hits = post["hits"] - pre["hits"]
    misses = post["misses"] - pre["misses"]
    evictions = (post.get("evictions", post.get("removals", 0))
                 - pre.get("evictions", pre.get("removals", 0)))
    expirations = post["expirations"] - pre["expirations"]
    run_hit_rate = hits / max(1, (hits + misses))

    print("TimedLRUCache Benchmark (multi-thread)")
    print(f"  Threads: {threads}, Capacity: {capacity}, TTL: {ttl}s, Working set: {n_keys}, Read ratio: {int(read_ratio*100)}%")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Ops: {total_ops:,}  (gets: {total_gets:,}, sets: {total_sets:,})")
    print(f"  Throughput: {int(total_ops / max(wall, 1e-9)):,} ops/sec")
    print(f"  Hit rate: {run_hit_rate*100:.2f}%  Evictions: {evictions}  Expirations: {expirations}")
    print(f"  Final stats: {post}")

if __name__ == "__main__":
    bench_multi()
