import requests
import json
import time
import os
import logging

addr = 'http://localhost:5000'
test_url = addr + '/api/gethssstatus'
response = ""
notrunningcount = 0
#LOG_FILE = 'logs/WebApp.log'
# send http request with image and receive response
while True:
   try:
      response3 = requests.get(test_url)
      response2 = json.loads(response3.text)
      response1 = json.dumps(response2)
      response = json.loads(response1)
   except:
      response2 = {"status": "NOT running"}
      response1 = json.dumps(response2)
      response = json.loads(response1)
   if response['status'] == "NOT running":
      notrunningcount = notrunningcount +1
      print('WebApp not reacheable. Attempt (out of 4 before restarting): '+ str(notrunningcount))
   time.sleep(3)

   if notrunningcount > 3:
      print("Restart WebApp.py")
      os.system("python WebApp.py")
      notrunningcount =0
