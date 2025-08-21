import time
from reliabilipy import throttle, Throttled


# Allow 5 calls per second with small bursts, sleep mode
@throttle(calls=5, period=1.0, burst=5, mode="sleep")
def do_work(i):
    print(f"work {i} at {time.time():.3f}")


# Allow 2 calls per second, raise when exceeded
@throttle(calls=2, period=1.0, mode="raise")
def limited_api(i):
    print(f"api {i} at {time.time():.3f}")


def main():
    print("Sleep-mode throttle (5 calls/sec):")
    t0 = time.time()
    for i in range(12):
        do_work(i)
    print(f"Elapsed ~{time.time() - t0:.2f}s for 12 calls\n")

    print("Raise-mode throttle (2 calls/sec):")
    successes = 0
    failures = 0
    for i in range(6):
        try:
            limited_api(i)
            successes += 1
        except Throttled as e:
            failures += 1
            print(f"throttled at i={i}: {e}")
    print(f"successes={successes}, failures={failures}")


if __name__ == "__main__":
    main()
