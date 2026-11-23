from scapy.all import sniff, IP
import time
from collections import defaultdict
from sklearn.ensemble import IsolationForest
import numpy as np
import paho.mqtt.client as mqtt

# MQTT setup (connect to fog)
client = mqtt.Client()
client.connect("test.mosquitto.org", 1883, 60)

packet_count = 0
ip_count = defaultdict(int)
start_time = time.time()

# ML model
model = IsolationForest(contamination=0.1)
data_buffer = []

def process_packet(packet):
    global packet_count, start_time
    
    if IP in packet:
        src_ip = packet[IP].src
        ip_count[src_ip] += 1
        packet_count += 1

    current_time = time.time()

    if current_time - start_time >= 1:
        print("\nPackets in last second:", packet_count)

        # Feature extraction
        unique_ips = len(ip_count)
        max_ip_packets = max(ip_count.values()) if ip_count else 0

        features = [packet_count, unique_ips, max_ip_packets]
        data_buffer.append(features)

        # Rule-based detection
        if packet_count > 1000:
            print("⚠️ High traffic detected!")
            client.publish("ddos/alerts", "High traffic detected at edge!")

        for ip, count in ip_count.items():
            if count > 200:
                print(f"🚨 Suspicious IP detected: {ip} -> {count} packets")
                client.publish("ddos/alerts", f"Suspicious IP: {ip} with {count} packets")

        # ML detection
        if len(data_buffer) > 10:
            X = np.array(data_buffer)
            model.fit(X)

            prediction = model.predict([features])

            if prediction[0] == -1:
                print("🚨 ML DETECTED ANOMALY")
                client.publish("ddos/alerts", "ML anomaly detected at edge!")

        # Reset
        packet_count = 0
        ip_count.clear()
        start_time = current_time


print("Starting EDGE node with ML + Fog connection...")

sniff(prn=process_packet, store=0)