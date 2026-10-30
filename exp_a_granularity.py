#!/usr/bin/env python3
"""Experiment A: granularity trap. chunksize=1 (micro-tasks) vs chunksize=10_000 (coarse)."""
import argparse
import statistics
import time
from multiprocessing import Pool

PS = (1, 2, 4, 8)


def collatz_steps(n):
    steps = 0
    while n > 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def run_granularity(workers, total_items=1_000_000, chunk_size=1):
    numbers = range(1, total_items + 1)
    t0 = time.perf_counter()
    with Pool(processes=workers) as pool:
        # chunk_size=1 creates one IPC task envelope per number (micro-tasks)
        results = pool.map(collatz_steps, numbers, chunksize=chunk_size)
    return time.perf_counter() - t0, sum(results)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--total", type=int, default=1_000_000)
    ap.add_argument("--repeats", type=int, default=1, help="median of N runs (fine mode is slow)")
    ap.add_argument("--chunks", type=int, nargs="+", default=[1, 10_000])
    a = ap.parse_args()

    for k in a.chunks:
        T, checksum = {}, None
        for p in PS:
            runs = []
            for _ in range(a.repeats):
                t, s = run_granularity(p, a.total, k)
                assert checksum in (None, s), "result changed between runs!"
                checksum = s
                runs.append(t)
            T[p] = statistics.median(runs)
        t1 = T[1]
        print(f"\n--- chunksize={k} (checksum {checksum}) ---")
        e = {}
        print(f"P= 1 | Time={t1:7.3f}s")
        for p in PS[1:]:
            e[p] = ((p * T[p] / t1) - 1.0) / (p - 1.0)
            print(f"P={p:2d} | Time={T[p]:7.3f}s | Speedup={t1/T[p]:5.2f}x | "
                  f"Eff={t1/T[p]/p*100:5.1f}% | Karp-Flatt e={e[p]:6.3f}")
        label = "A: Micro (k=1)" if k == 1 else f"A: Coarse (k={k})"
        print(f"| {label} | {T[1]:.3f} | {T[2]:.3f} | {T[4]:.3f} | {T[8]:.3f} | {t1/T[8]:.2f} | {e[2]:.3f} | {e[8]:.3f} |")
