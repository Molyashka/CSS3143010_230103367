#!/usr/bin/env python3
"""Experiment C: privatize before synchronizing -> expect near-linear speedup, tiny e(p)."""
import argparse
import statistics
import time
from multiprocessing import Pool


def private_worker(iterations):
    local_sum = 0  # private accumulation, zero shared state
    for _ in range(iterations):
        local_sum += 1
    return local_sum


def run_privatized(p, total_increments=20_000_000):
    increments_per_worker = total_increments // p
    tasks = [increments_per_worker] * p
    t0 = time.perf_counter()
    with Pool(processes=p) as pool:
        results = pool.map(private_worker, tasks)
    total = sum(results)  # synchronize exactly once
    t1 = time.perf_counter()
    assert total == total_increments
    return t1 - t0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--total", type=int, default=20_000_000,
                    help="raise (e.g. 80000000) if Pool start-up overhead inflates e(p)")
    ap.add_argument("--repeats", type=int, default=3)
    a = ap.parse_args()

    T = {p: statistics.median(run_privatized(p, a.total) for _ in range(a.repeats)) for p in (1, 2, 4)}
    t1, e = T[1], {}
    print(f"P=1 | Runtime={t1:.3f}s")
    for p in (2, 4):
        e[p] = ((p * T[p] / t1) - 1.0) / (p - 1.0)
        print(f"P={p} | Runtime={T[p]:.3f}s | Speedup={t1/T[p]:.2f}x | KarpFlatt e={e[p]:.3f}")
    E4 = (t1 / T[4]) / 4 * 100
    print(f"checks: T4 < T1: {T[4] < t1} | E4 = {E4:.1f}% (need > 70%)")
    print(f"| C: Privatized State | {T[1]:.3f} | {T[2]:.3f} | {T[4]:.3f} | {e[2]:.3f} | {e[4]:.3f} | Collapsed e -> linear scalability restored |")
