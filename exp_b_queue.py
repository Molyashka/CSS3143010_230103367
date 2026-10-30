#!/usr/bin/env python3
"""Experiment B: every item crosses a multiprocessing.Queue -> IPC contention."""
import argparse
import statistics
import time
from multiprocessing import Process, Queue


def queue_worker(out_queue, items_per_worker):
    for i in range(items_per_worker):
        out_queue.put(i % 7)  # pathological: every iteration crosses an IPC boundary


def run_queue_benchmark(p, total_items=400_000):
    q = Queue()
    items_per_worker = total_items // p
    total_items = items_per_worker * p  # avoid a hang if total_items % p != 0
    workers = [Process(target=queue_worker, args=(q, items_per_worker)) for _ in range(p)]
    t0 = time.perf_counter()
    for w in workers:
        w.start()
    collected = 0
    while collected < total_items:  # master consumes everything from the shared channel
        _ = q.get()
        collected += 1
    for w in workers:
        w.join()
    return time.perf_counter() - t0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--total", type=int, default=400_000)
    ap.add_argument("--repeats", type=int, default=3)
    a = ap.parse_args()

    T = {p: statistics.median(run_queue_benchmark(p, a.total) for _ in range(a.repeats))
         for p in (1, 2, 4, 8)}
    t1, e = T[1], {}
    print("\n--- Queue Contention Karp-Flatt Analysis ---")
    print(f"P= 1 | Time={t1:6.3f}s | throughput={a.total/t1:,.0f} items/s")
    for p in (2, 4, 8):
        e[p] = ((p * T[p] / t1) - 1.0) / (p - 1.0)
        print(f"P={p:2d} | Time={T[p]:6.3f}s | Speedup={t1/T[p]:5.2f}x | Karp-Flatt e={e[p]:6.3f}")
    print(f"checks: T8 > T1: {T[8] > t1} | monotonic T rise: {T[1] < T[2] < T[4] < T[8]} "
          f"| e rising: {e[2] < e[4] < e[8]}")
    print(f"| B: Queue Choke | {T[1]:.3f} | {T[2]:.3f} | {T[4]:.3f} | {T[8]:.3f} | {t1/T[8]:.2f} | {e[2]:.3f} | {e[8]:.3f} |")
