from time import perf_counter_ns
from math import log

def fmt_ns(time_ns:int|float) -> str:
    for size, unit in enumerate('num '):
        if time_ns < 10**(size*3):
            return f'{time_ns/(10**(size*3)):.2f}{unit}s'
    return 'ages...'

def fmt_bytes(b:int):
    s = int(log(b,1024))
    p = ' kMGTPEZY'[s]
    f = b/1024**s
    return f"{f:.{1 if f%1 else 0}f} {p}B" if p!=' ' else f'{b} Bytes'

def timer(func):
    def wrapper(*args, **kwargs):
        start_ns = perf_counter_ns()
        res = func(*args, **kwargs)
        time_ns = perf_counter_ns() - start_ns
        print(f'{func.__name__} took {fmt_ns(time_ns)}')
        return res
    return wrapper

def time_func(func, *args, **kwargs):
    start_ns = perf_counter_ns()
    res = func(*args, **kwargs)
    time_ns = perf_counter_ns() - start_ns
    print(f'{func.__name__} took {fmt_ns(time_ns)}')
    return res

def x_per_sec(old_ns:int, amt:int|float, new_ns:int = perf_counter_ns()) -> str:
    amt_s:float = amt / ((new_ns-old_ns) / 1e9)
    scales = {
        '' : 1e0,
        'k' : 1e3,
        'm' : 1e6,
        'g' : 1e9,
    }
    for name, size in scales.items():
        if amt_s < size*1e3:
            return f'{amt_s/size:.1f}{name} terms / s'
    return 'too fast, cant count'

def speedtest(func):
    times = []
    start_wall = perf_counter_ns()

    def wrapper(*args, **kwargs):
        while perf_counter_ns() - start_wall < 3e9:
            start_ns = perf_counter_ns()
            func(*args, **kwargs)
            time_ns = perf_counter_ns() - start_ns
            times.append(time_ns)

        print(f'{len(times)}x{func.__name__} in ~3s | min:{fmt_ns(min(times))} | max:{fmt_ns(max(times))} | avg:{fmt_ns(sum(times)/len(times))}')
        # print(f'first: {fmt_ns(times[0])}')
    return wrapper