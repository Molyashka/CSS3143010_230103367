
EXP A 
--- chunksize=1 (checksum 131434424) ---
P= 1 | Time= 23.112s
P= 2 | Time= 23.089s | Speedup= 1.00x | Eff= 50.0% | Karp-Flatt e= 0.998
P= 4 | Time= 25.827s | Speedup= 0.89x | Eff= 22.4% | Karp-Flatt e= 1.157
P= 8 | Time= 29.776s | Speedup= 0.78x | Eff=  9.7% | Karp-Flatt e= 1.330
| A: Micro (k=1) | 23.112 | 23.089 | 25.827 | 29.776 | 0.78 | 0.998 | 1.330 |

--- chunksize=10000 (checksum 131434424) ---
P= 1 | Time= 13.233s
P= 2 | Time=  8.364s | Speedup= 1.58x | Eff= 79.1% | Karp-Flatt e= 0.264
P= 4 | Time=  4.279s | Speedup= 3.09x | Eff= 77.3% | Karp-Flatt e= 0.098
P= 8 | Time=  3.371s | Speedup= 3.93x | Eff= 49.1% | Karp-Flatt e= 0.148
| A: Coarse (k=10000) | 13.233 | 8.364 | 4.279 | 3.371 | 3.93 | 0.264 | 0.148 |

EXP B
--- Queue Contention Karp-Flatt Analysis ---
P= 1 | Time= 5.477s | throughput=73,032 items/s
P= 2 | Time= 7.938s | Speedup= 0.69x | Karp-Flatt e= 1.899
P= 4 | Time= 4.561s | Speedup= 1.20x | Karp-Flatt e= 0.777
P= 8 | Time= 5.041s | Speedup= 1.09x | Karp-Flatt e= 0.909
checks: T8 > T1: False | monotonic T rise: False | e rising: False
| B: Queue Choke | 5.477 | 7.938 | 4.561 | 5.041 | 1.09 | 1.899 | 0.909 |



EXP C
P= 1 | Time= 1.326s | throughput=7,542,076 items/s
P= 2 | Time= 0.820s | Speedup= 1.62x | Eff= 80.8% | Karp-Flatt e= 0.237
P= 4 | Time= 0.682s | Speedup= 1.94x | Eff= 48.6% | Karp-Flatt e= 0.352
P= 8 | Time= 0.569s | Speedup= 2.33x | Eff= 29.1% | Karp-Flatt e= 0.348
checks: S8 = 2.33 (need > 5.0) | e(8) = 0.348 (need <= 0.05)
Compare throughput with Exp B's P=1 items/s for the >10x claim.
| C: Buffered Batch | 1.326 | 0.820 | 0.682 | 0.569 | 2.33 | 0.237 | 0.348 |
