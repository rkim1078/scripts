import csv, os, signal, socket, sys, time
from datetime import datetime

# Two independent targets: a drop is only logged if BOTH fail,
# so one host having a bad moment doesn't create a false outage.
TARGETS = [("1.1.1.1", 53), ("8.8.8.8", 53)]
TARGET_LABEL = "|".join(h for h, _ in TARGETS)

INTERVAL_UP = 10    # seconds between checks while the connection is healthy
INTERVAL_DOWN = 2   # check faster during an outage for better restore-time accuracy
TIMEOUT = 2         # seconds to wait per target
LOGFILE = "wifi_drops.csv"


def is_up():
    """TCP connect to a DNS server. No subprocess spawn, same code on every OS."""
    for host, port in TARGETS:
        try:
            with socket.create_connection((host, port), timeout=TIMEOUT):
                return True
        except OSError:
            continue
    return False


def log_row(row):
    # Open/append/close per event: events are rare, and nothing is lost on a crash.
    with open(LOGFILE, "a", newline="") as f:
        csv.writer(f).writerow(row)


def ts(dt):
    return dt.isoformat(timespec="seconds")


def main():
    # Lower our scheduling priority where supported (Linux/macOS).
    if hasattr(os, "nice"):
        try:
            os.nice(10)
        except OSError:
            pass

    # Treat SIGTERM (systemd stop, task manager, etc.) like Ctrl+C so cleanup runs.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    if not os.path.exists(LOGFILE):
        log_row(["drop_time", "restore_time", "duration_sec", "target"])

    down_wall = None   # wall-clock time for the log
    down_mono = None   # monotonic time for the duration (immune to clock changes)
    print(f"Monitoring {TARGET_LABEL}... Ctrl+C to stop.")

    try:
        while True:
            up = is_up()

            if not up and down_mono is None:
                down_wall, down_mono = datetime.now(), time.monotonic()
                print(f"[{down_wall:%H:%M:%S}] DROP detected")
            elif up and down_mono is not None:
                now = datetime.now()
                duration = time.monotonic() - down_mono
                log_row([ts(down_wall), ts(now), round(duration, 1), TARGET_LABEL])
                print(f"[{now:%H:%M:%S}] Restored after {duration:.0f}s")
                down_wall = down_mono = None

            time.sleep(INTERVAL_DOWN if down_mono is not None else INTERVAL_UP)
    except KeyboardInterrupt:
        pass
    finally:
        if down_mono is not None:
            duration = time.monotonic() - down_mono
            log_row([ts(down_wall), "still down at exit", round(duration, 1), TARGET_LABEL])
        print("\nStopped monitoring.")


if __name__ == "__main__":
    main()
