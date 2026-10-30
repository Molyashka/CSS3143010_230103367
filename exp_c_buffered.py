#!/usr/bin/env python3
"""Experiment C: workers aggregate into a private buffer and flush batches to the queue."""
import argparse
import statistics
import time
from multiprocessing import Process, Queue


def buffered_worker(out_queue, items_per_worker, batch_size=10_000):
    buffer = []
    for i in range(items_per_worker):
        buffer.append(i % 7)
        if len(buffer) >= batch_size:
            out_queue.put(sum(buffer))  # one pre-aggregated flush per batch
            buffer.clear()
    if buffer:
        out_queue.put(sum(buffer))
    out_queue.put(None)  # sentinel: end of work


def run_buffered(p, total_items=10_000_000):
    q = Queue()
    items_per_worker = total_items // p
    workers = [Process(target=buffered_worker, args=(q, items_per_worker)) for _ in range(p)]
    t0 = time.perf_counter()
    for w in workers:
        w.start()
    total_sum, active = 0, p
    while active > 0:
        val = q.get()
        if val is None:
            active -= 1
        else:
            total_sum += val
    for w in workers:
        w.join()
    return time.perf_counter() - t0, total_sum


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--total", type=int, default=10_000_000)
    ap.add_argument("--repeats", type=int, default=3)
    a = ap.parse_args()

    T, checksum = {}, None
    for p in (1, 2, 4, 8):
        runs = []
        for _ in range(a.repeats):
            t, s = run_buffered(p, a.total)
            expected = sum(i % 7 for i in range(a.total // p)) * p
            assert s == expected, f"wrong sum for P={p}: {s} != {expected}"
            runs.append(t)
        T[p] = statistics.median(runs)
    t1, e = T[1], {}
    print(f"P= 1 | Time={t1:6.3f}s | throughput={a.total/t1:,.0f} items/s")
    for p in (2, 4, 8):
        e[p] = ((p * T[p] / t1) - 1.0) / (p - 1.0)
        print(f"P={p:2d} | Time={T[p]:6.3f}s | Speedup={t1/T[p]:5.2f}x | "
              f"Eff={t1/T[p]/p*100:5.1f}% | Karp-Flatt e={e[p]:6.3f}")
    print(f"checks: S8 = {t1/T[8]:.2f} (need > 5.0) | e(8) = {e[8]:.3f} (need <= 0.05)")
    print("Compare throughput with Exp B's P=1 items/s for the >10x claim.")
    print(f"| C: Buffered Batch | {T[1]:.3f} | {T[2]:.3f} | {T[4]:.3f} | {T[8]:.3f} | {t1/T[8]:.2f} | {e[2]:.3f} | {e[8]:.3f} |")
