import paho.mqtt.client as mqtt
import time, threading, ssl

class MQTTClient(object):
   

   def __init__(self,clientId, serverhost):  
      self.client = mqtt.Client(client_id=clientId)
      self.client.on_publish = self.on_publish
      #self.client.on_message = self.on_message
      self.client.connect(serverhost, 1883)
      self.client.loop_start()
      self.receivedMessages = []

   def subscribe(self, topic):
      self.client.subscribe(topic)

   def publish(self,topic, message, waitForAck = False):
      mid = self.client.publish(topic, message, 2)[1]
      if (waitForAck):
        while mid not in self.receivedMessages:
          time.sleep(0.25)

   def on_publish(self,client, userdata, mid):
      self.receivedMessages.append(mid)

#   def on_message(self, client, userdata, message):
#      print("Received message " + str(message.payload))
#    if (message.payload.startswith("510")):
#       print("Simulating device restart...")
        
