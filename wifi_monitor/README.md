software made for Windows

needed a way to cleanly detect wifi connection drops

usage:
```
python wifi_monitor.py
```

outputs into `wifi_drops.csv`, telling you the timestamp of when the connection was dropped, when connection was restored, time gap between connection dropped and restored, and the target being pinged

checks Cloudflare DNS every 1s. you can change the lines in the code to target different DNS, poll more/less frequently, or the outfile here:
```
TARGET = "1.1.1.1"  # i.e., 8.8.8.8
INTERVAL = 1  # 0.5, 2, etc.
LOGFILE = "wifi_drops.csv"
```

changelog:
- added `wifi_drops_efficient.csv`, slightly modified version for running on a device for multiple days. `ping()` forks an entirely new process every call, changed to just open a TCP connection on port 53 on 1.1.1.1, 8.8.8.8 instead, which is just a few syscalls within the already running python process as opposed to another process lifecycle using `ping()`. adaptively polls every 10s when no drops detected, bumps up to 2s during an outage. also uses os.nice() so it yields to other processes