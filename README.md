# Edge–Fog DDoS Detection

A three-tier **Edge → Fog → Cloud** system for spotting DDoS attacks in real time. The edge node sniffs live network traffic and flags suspicious activity with both simple rules and an unsupervised ML model. Alerts travel over MQTT to a fog node and to a cloud dashboard.

```
 ┌──────────────┐   MQTT: ddos/alerts   ┌──────────────┐
 │  Edge node   │ ────────────────────▶ │   Fog node   │  prints alerts locally
 │  edge.py     │           │           │   fog.py     │
 │ sniff + ML   │           │           └──────────────┘
 └──────────────┘           │           ┌──────────────┐
                            └─────────▶ │  Cloud node  │  Flask dashboard
                                        │  cloud.py    │  http://127.0.0.1:5000
                                        └──────────────┘
```

## How detection works

The edge node collects these features over each 1-second window:

| Feature | Meaning |
| --- | --- |
| `packet_count` | Total IP packets seen in the window |
| `unique_ips` | Number of distinct source IPs |
| `max_ip_packets` | Packets from the single busiest source IP |

It then raises an alert in three ways:

1. **High traffic (rule):** more than 1,000 packets in a second.
2. **Suspicious IP (rule):** a single source IP sends more than 200 packets in a second.
3. **ML anomaly:** an [Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html) is fitted on the recent windows once it has more than 10 samples. Any window it scores as an outlier is reported.

Each alert is published to the `ddos/alerts` topic on the public `test.mosquitto.org` broker. The fog node prints the alerts it receives. The cloud node stores them and shows them on a dashboard that refreshes every 2 seconds. Alerts are colour-coded: red for ML anomalies, yellow for high traffic, orange for suspicious IPs.

## Tech stack

- Python 3
- [Scapy](https://scapy.net/) for packet capture
- scikit-learn (Isolation Forest) + NumPy
- [Eclipse Paho](https://pypi.org/project/paho-mqtt/) MQTT client
- Flask + Jinja2 for the dashboard

## Getting started

### Prerequisites

- Python 3.10+
- **Packet capture driver:** [Npcap](https://npcap.com/) on Windows (install with "WinPcap API-compatible mode"). On Linux/macOS, libpcap is usually already installed.
- Admin / root rights for the edge node, since sniffing packets needs them.

### Install

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### Run

Start each tier in its own terminal, from the project folder:

```bash
# 1. Cloud dashboard → open http://127.0.0.1:5000
python cloud.py

# 2. Fog node
python fog.py

# 3. Edge node (run as Administrator / with sudo)
python edge.py
```

To see alerts, generate some traffic, for example a burst of pings or a load-testing tool against a machine you own.

## Project structure

```
edge.py              Edge node: packet sniffing, feature extraction, rules + Isolation Forest
fog.py               Fog node: subscribes to alerts
cloud.py             Cloud node: Flask app that collects and displays alerts
templates/index.html Dashboard UI
requirements.txt
```

## Notes

- `test.mosquitto.org` is a **public** broker, so anyone can read or publish to `ddos/alerts`. For anything beyond a demo, run your own broker (e.g. Mosquitto) and change the host in all three scripts.
- The thresholds (1,000 packets/s, 200 packets/IP/s, 10% contamination) are demo values. Tune them for your network.
