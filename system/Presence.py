import subprocess
from time import sleep
from threading import Thread
import os
import ConfigParser
import io
import paho.mqtt.client as mqtt
import json
import time, threading, ssl
import MQTTClient
from datetime import datetime
from ConfigParser import SafeConfigParser

#RdL Load Params from HSConfig.cfg
hsconfigparser = SafeConfigParser()
hsconfigparser.read('HSConfig.cfg')
param_mqttbroker = hsconfigparser.get('MQTT', 'broker')
param_mqttport = hsconfigparser.get('MQTT', 'port')
param_mqttnetworkchannel = hsconfigparser.get('MQTT', 'publishnetwork')
param_networkscan_rememberstate = hsconfigparser.get('NETWORKSCAN', 'rememberstate')



# Function that gets name from all Persona.cfg files in the /aligned-images folder
def get_names():                                                                                                  
    r = []
    persona_name = []                                                                                                          
    filenames= os.listdir ("./aligned-images")
    for filename in filenames: # loop through all the files and folders
        if os.path.isdir(os.path.join(os.path.abspath("./aligned-images"), filename)):                                                                                           
            if os.path.isfile(os.path.join(os.path.abspath("./aligned-images"), filename,"Persona.cfg")):
                with open(os.path.join(os.path.abspath("./aligned-images"), filename,"Persona.cfg")) as f:
                    persona_config = f.read()
                    config = ConfigParser.RawConfigParser(allow_no_value=True)
                    config.readfp(io.BytesIO(persona_config))
                    persona_name.append(config.get('persona', 'nickname'))                                                                   
    return persona_name 

# Function that gets mac address from all Persona.cfg files in the /aligned-images folder
def get_macs():                                                                                                  
    r = []
    persona_mac = []                                                                                                          
    filenames= os.listdir ("./aligned-images")
    for filename in filenames: # loop through all the files and folders
        if os.path.isdir(os.path.join(os.path.abspath("./aligned-images"), filename)):                                                                                           
            if os.path.isfile(os.path.join(os.path.abspath("./aligned-images"), filename,"Persona.cfg")):
                with open(os.path.join(os.path.abspath("./aligned-images"), filename,"Persona.cfg")) as f:
                    persona_config = f.read()
                    config = ConfigParser.RawConfigParser(allow_no_value=True)
                    config.readfp(io.BytesIO(persona_config))
                    persona_mac.append(config.get('persona', 'phonemac'))                                                                   
    return persona_mac 

def arpnetworkscan():
   # Edit these for how many people/devices you want to track
   # occupant = ["Rachel","Jamie","Broc","Adam","Jeff","Raymond","David","Kaylee"]
   #occupant = ["Ronald"]
   global output
   output = ""
   #MQTTClient = MQTTClient.MQTTClient("2","192.168.178.100")
   global occupant 
   occupant = get_names()
   #print occupant

   # MAC addresses for our phones
   #address = ["xx:xx:xx:xx:xx:xx","xx:xx:xx:xx:xx:xx","xx:xx:xx:xx:xx:xx","xx:xx:xx:xx:xx:xx","xx:xx:xx:xx:xx:xx","xx:xx:xx:xx:xx:xx","xx:xx:xx:xx:xx:xx","xx:xx:xx:xx:xx:xx"]
   #address = ["78:88:6d:26:24:12"]
   global address 
   address = get_macs()
   #print address
   # Sleep once right when this script is called to give the Pi enough time
   # to connect to the network
   #sleep(60)

   # Initialize the Initial State streamer
   # Be sure to add your unique access key
   # streamer = Streamer(bucket_name=":office:Who's at the Office?", bucket_key="office_presence", access_key="rdl")

   # Some arrays to help minimize streaming and account for devices   
   # disappearing from the network when asleep
   global firstRun
   global presentSent
   global notPresentSent
   global counter
   firstRun = [1] * len(occupant)
   presentSent = [0] * len(occupant)
   notPresentSent = [0] * len(occupant)
   counter = [0] * len(occupant)
   #print((os.path.dirname(os.path.abspath(__file__)))+"/aligned-images/")
   global ARPMQTTClient
   ARPMQTTClient = MQTTClient.MQTTClient("2",param_mqttbroker,param_mqttport)
   # Main thread

   try:

       # Initialize a variable to trigger threads to exit when True
       #global output
       global stop
       stop = False

       # Start the thread(s)
       # It will start as many threads as there are values in the occupant array
       for i in range(len(occupant)):
           t = Thread(target=whosHere, args=(i,))
           t.start()

       while True:
           # Make output global so the threads can see it
           #global output
           # Assign list of devices on the network to "output"
           interface = subprocess.check_output("/sbin/route -n | grep '^0.0.0.0' | rev | cut -d' ' -f1 | rev", shell=True)
           command = "sudo arp-scan -l --interface="+interface
           output = subprocess.check_output(command, shell=True)
           # Wait 30 seconds between scans
           sleep(30)
   except KeyboardInterrupt:
      # On a keyboard interrupt signal threads to exit
      stop = True
   exit()

def broadcast_message_log(broadcastmessage):
   temp = broadcastmessage.split("@")
   person = temp[0]
   network = temp[1]
   #print person
   #print network
   mqttmessage = {'person':person,'network':network}
   ARPMQTTClient.publish(param_mqttnetworkchannel,json.dumps(mqttmessage), True)
   #client.close()
   broadcastmessage = datetime.now().strftime("%b %d %Y %H:%M") +": "+broadcastmessage+"\n"	
   #print(broadcastmessage)	
   #broadcastmessage = "This is a test broadcast"
   if not os.path.exists('broadcast.log'):
      with open('broadcast.log', 'w'): pass
   #filetemp.close()        
   f = open('broadcast.log','r+')
   lines = f.readlines() # read old content
   f.seek(0) # go back to the beginning of the file
   f.write(broadcastmessage) # write new content at the beginning
   for line in lines: # write old content after new
      f.write(line)
   f.close()
              
# Function that checks for device presence
def whosHere(i):
    
    # 30 second pause to allow main thread to finish arp-scan and populate output
    sleep(30)

    # Loop through checking for devices and counting if they're not present
    while True:

        # Exits thread if Keyboard Interrupt occurs
        if stop == True:
            #print "Exiting Thread"
            exit()
        else:
            pass

        # If a listed device address is present print and stream
        if address[i] in output:
            #print(occupant[i] + "'s device is connected to your network")
            if presentSent[i] == 0:
                # Stream that device is present
                # streamer.log(occupant[i],":office:")
                # streamer.flush()
                #print(occupant[i] + " present streamed")
                broadcast_message_log(occupant[i]+"@Connected")
		#mqttmessage = {'person':occupant[i],'network':"Present"}
		#ARPMQTTClient.publish("homesurveillance/network", json.dumps(mqttmessage), True)
		#MQTTClient.publish("home/presence", json.dumps(mqttmessage), True)
                # Reset counters so another stream isn't sent if the device
                # is still present
                firstRun[i] = 0
                presentSent[i] = 1
                notPresentSent[i] = 0
                counter[i] = 0
                sleep(int(param_networkscan_rememberstate))
            else:
                # If a stream's already been sent, just wait for x seconds
                counter[i] = 0
                sleep(int(param_networkscan_rememberstate))
        # If a listed device address is not present, print and stream
        else:
            #print(occupant[i] + "'s device is not present")
            # Only consider a device offline if it's counter has reached 30
            # This is the same as 15 minutes passing
            if counter[i] == 30 or firstRun[i] == 1:
                firstRun[i] = 0
                if notPresentSent[i] == 0:
                    # Stream that device is not present
                    # streamer.log(occupant[i],":no_entry_sign::office:")
                    # streamer.flush()
                    #print(occupant[i] + " not present streamed")
                    broadcast_message_log(occupant[i]+"@Disconnected")
                    #mqttmessage = {'person':occupant[i],'network':"NOT Present"}
		    #ARPMQTTClient.publish("homesurveillance/network", json.dumps(mqttmessage), True)
                    # Reset counters so another stream isn't sent if the device
                    # is still present
                    notPresentSent[i] = 1
                    presentSent[i] = 0
                    counter[i] = 0
                else:
                    # If a stream's already been sent, wait 30 seconds
                    counter[i] = 0
                    sleep(30)
            # Count how many 30 second intervals have happened since the device 
            # disappeared from the network
            else:
                counter[i] = counter[i] + 1
                #print(occupant[i] + "'s counter at " + str(counter[i]))
                sleep(30)





