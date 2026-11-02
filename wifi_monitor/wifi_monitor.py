import subprocess, platform, time, csv, os
from datetime import datetime

TARGET = "1.1.1.1"  # Cloudflare DNS; also try 8.8.8.8
INTERVAL = 1  # seconds between checks
LOGFILE = "wifi_drops.csv"

def is_up():
    flag = "-n" if platform.system() == "Windows" else "-c"
    timeout = ["-w", "2000"] if platform.system() == "Windows" else ["-W", "2"]
    result = subprocess.run(["ping", flag, "1", *timeout, TARGET],
                            capture_output=True)
    return result.returncode == 0

if not os.path.exists(LOGFILE):
    with open(LOGFILE, "w", newline="") as f:
        csv.writer(f).writerow(["drop_time", "restore_time", "duration_sec", "target"])

down_since = None
print(f"Monitoring {TARGET}... Ctrl+C to stop.")

try:
    while True:
        up = is_up()
        now = datetime.now()
        if not up and down_since is None:
            down_since = now
            print(f"[{now:%H:%M:%S}] DROP detected")
        elif up and down_since is not None:
            duration = (now - down_since).total_seconds()
            with open(LOGFILE, "a", newline="") as f:
                csv.writer(f).writerow([down_since.isoformat(timespec="seconds"),
                                        now.isoformat(timespec="seconds"),
                                        round(duration, 1), TARGET])
            print(f"[{now:%H:%M:%S}] Restored after {duration:.0f}s")
            down_since = None
        time.sleep(INTERVAL)
except KeyboardInterrupt:
    now = datetime.now()
    if down_since is not None:
        duration = (now - down_since).total_seconds()
        with open(LOGFILE, "a", newline="") as f:
            csv.writer(f).writerow([down_since.isoformat(timespec="seconds"),
                                    "still down at exit",
                                    round(duration, 1), TARGET])
    print("\nStopped monitoring.")
