from flask import Flask, render_template
import paho.mqtt.client as mqtt
from datetime import datetime
import os

# Ensure Flask finds templates folder correctly
app = Flask(__name__, template_folder=os.path.join(os.getcwd(), "templates"))

alerts = []

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe("ddos/alerts")

def on_message(client, userdata, msg):
    alert = msg.payload.decode()
    print("Cloud received:", alert)
    
    alerts.append({
        "message": alert,
        "time": datetime.now().strftime("%H:%M:%S")
    })

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Make sure this matches your edge.py
client.connect("test.mosquitto.org", 1883, 60)

client.loop_start()

@app.route('/')
def home():
    return render_template("index.html", alerts=alerts[::-1])

if __name__ == '__main__':
    app.run(debug=True)