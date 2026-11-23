import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code:", rc)
    print("Fog connected to broker")
    client.subscribe("ddos/alerts")

def on_message(client, userdata, msg):
    print("\n🚨 ALERT RECEIVED AT FOG:")
    print(msg.payload.decode())

    

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

print("Fog node running...")

client.connect("test.mosquitto.org", 1883, 60)

client.loop_forever()