import requests
import json
import time
import os

addr = 'http://localhost:5000'
test_url = addr + '/api/gethssstatus'
response = ""
notrunningcount = 0
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
      print notrunningcount
   time.sleep(3)

   if notrunningcount > 3:
      print("Restart WebApp.py")
      os.system("python WebApp.py")
      notrunningcount =0
