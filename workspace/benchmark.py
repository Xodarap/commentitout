# Benchmark template
import time
import numpy as np

def benchmark_function(func, *args, iterations=1000):
    times = []
    for _ in range(iterations):
        start = time.time()
        func(*args)
        times.append(time.time() - start)
    return {
        'mean': np.mean(times),
        'std': np.std(times),
        'min': np.min(times),
        'max': np.max(times)
    }
