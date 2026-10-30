#!/usr/bin/env python3
"""Experiment A: stubborn serial tail (0.40 s sequential sleep) -> expect flat e(p)."""
import argparse
import math
import statistics
import time
from multiprocessing import Pool


def heavy_math(n):
    return sum(math.sin(i) * math.cos(i) for i in range(1, n))


def run_experiment(workers, total_chunks=16, chunk_size=2_000_000):
    t0 = time.perf_counter()
    time.sleep(0.40)  # Intentional sequential bottleneck
    with Pool(processes=workers) as pool:
        pool.map(heavy_math, [chunk_size] * total_chunks)
    return time.perf_counter() - t0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunk-size", type=int, default=2_000_000)
    ap.add_argument("--repeats", type=int, default=3)
    a = ap.parse_args()

    T = {p: statistics.median(run_experiment(p, chunk_size=a.chunk_size) for _ in range(a.repeats))
         for p in (1, 2, 4)}
    t1, e = T[1], {}
    print(f"P=1 | Runtime={t1:.3f}s")
    for p in (2, 4):
        sp = t1 / T[p]
        e[p] = ((p * T[p] / t1) - 1.0) / (p - 1.0)
        print(f"P={p} | Runtime={T[p]:.3f}s | Speedup={sp:.2f}x | KarpFlatt e={e[p]:.3f}")
    print(f"e(4)/e(2) = {e[4]/e[2]:.2f}   (instructor check: within [0.80, 1.25])")
    print(f"| A: Serial Tail | {T[1]:.3f} | {T[2]:.3f} | {T[4]:.3f} | {e[2]:.3f} | {e[4]:.3f} | Constant e -> fixed Amdahl serialization |")
