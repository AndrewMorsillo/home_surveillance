import requests
import json

addr = 'http://localhost:1880'
test_url = addr + '/facebox/check'

# prepare headers for http request
content_type = 'image/jpeg'
headers = {'content-type': content_type}

img = open('uploads/imgs/ronald.jpeg', 'rb').read()


# send http request with image and receive response
response = requests.post(test_url, data=img, headers=headers)
# decode response
#print(response)
print json.loads(response.text)

# expected output: {u'message': u'image received. size=124x124'}
