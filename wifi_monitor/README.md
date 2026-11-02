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
