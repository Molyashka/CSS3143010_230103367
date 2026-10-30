#!/usr/bin/env python3
"""Experiment B: every increment takes a shared lock -> expect T4 > T1 and surging e(p)."""
import argparse
import statistics
import time
from multiprocessing import Process, Value, Lock


def contended_worker(shared_counter, lock, iterations):
    for _ in range(iterations):
        with lock:  # heavy lock contention & cache-line bouncing
            shared_counter.value += 1


def run_contended(p, total_increments=2_000_000):
    increments_per_worker = total_increments // p
    counter = Value('i', 0)
    lock = Lock()
    procs = [Process(target=contended_worker, args=(counter, lock, increments_per_worker))
             for _ in range(p)]
    t0 = time.perf_counter()
    for proc in procs:
        proc.start()
    for proc in procs:
        proc.join()
    t1 = time.perf_counter()
    assert counter.value == total_increments
    return t1 - t0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--total", type=int, default=2_000_000)
    ap.add_argument("--repeats", type=int, default=3)
    a = ap.parse_args()

    T = {p: statistics.median(run_contended(p, a.total) for _ in range(a.repeats)) for p in (1, 2, 4)}
    t1, e = T[1], {}
    print(f"P=1 | Runtime={t1:.3f}s")
    for p in (2, 4):
        tp = T[p]
        e[p] = ((p * tp / t1) - 1.0) / (p - 1.0)
        print(f"P={p} | Runtime={tp:.3f}s | Speedup={t1/tp:.2f}x | KarpFlatt e={e[p]:.3f}")
    print(f"checks: T4 > T1: {T[4] > t1} | e(4) >> e(2): {e[4]:.2f} vs {e[2]:.2f}")
    print(f"| B: Lock Contention | {T[1]:.3f} | {T[2]:.3f} | {T[4]:.3f} | {e[2]:.3f} | {e[4]:.3f} | Exploding e -> mutex & bus thrashing |")
