from flask import Flask, render_template, request, Response, stream_with_context
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from datetime import datetime
import time
import random
import json
import urllib.request

from jinja2.utils import urlize

app = Flask(__name__)

temp_val = 0
moisture_val = 0
methane_val = 0
last_mail = 0
temp_verdict = "LOW"
moisture_verdict = "HIGH"
methane_verdict = "NORMAL"
pop_verdict = "LOW"

def iot_handler(self, params, packet):
	print(packet.topic)
	print((packet.payload))
	json_data = json.loads(packet.payload)
	global temp_val, moisture_val, methane_val
	temp_val = float(json_data["Temperature"])
	moisture_val = float(json_data["Humidity"])
	methane_val = float(json_data["CH4 conc"])
	print(temp_val)

myMQTTClient = AWSIoTMQTTClient("random-client") #random key, if another connection using the same key is opened the previous one is auto closed by AWS IOT
myMQTTClient.configureEndpoint("a1r149u415pa4r-ats.iot.us-east-2.amazonaws.com", 8883) #endpoint 1
myMQTTClient.configureCredentials("root-ca.pem", "private.pem.key", "certificate.pem.crt")

myMQTTClient.configureOfflinePublishQueueing(-1) # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2) # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10) # 10 sec
# myMQTTClient.configureMQTTOperationTimeout(5) # 5 sec
print ('Connecting to AWS IoT Core....')

myMQTTClient.connect()
myMQTTClient.subscribe("outTopic", 1, iot_handler) #topic name

@app.route('/')
def index():
	city = "chennai"
	api_key =  "aa68e9cc745c091e290b5b054a659d88"
	coord = urllib.request.urlopen('https://api.openweathermap.org/geo/1.0/direct?q=' + city + '&limit=5&appid=' + api_key).read()
	lat_lon = json.loads(coord)
	lat=str(lat_lon[0]['lat'])
	lon=str(lat_lon[0]['lon'])


	source = urllib.request.urlopen('https://api.openweathermap.org/data/2.5/onecall?lat=' + lat + '&lon=' + lon + '&exclude=current,minutely&appid='+api_key).read()
	list_of_data = json.loads(source)
	pop = list_of_data["daily"][0]["pop"]
 
	print(pop)
	return render_template("chart-handler.html",pop=pop, pop_verdict=pop_verdict)

@app.route('/temp_handler')
def temp_handler():
	def generate_data(): 
		while True:
			json_data = json.dumps(
					{'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': temp_val})
			yield f"data:{json_data}\n\n"
			time.sleep(5)
	return Response(generate_data(), mimetype='text/event-stream')


@app.route('/moisture_handler')
def moisture_handler():
	def generate_data(): 
		while True:
			json_data = json.dumps(
					{'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': moisture_val})
			yield f"data:{json_data}\n\n"
			time.sleep(5)
	return Response(generate_data(), mimetype='text/event-stream')


@app.route('/methane_handler')
def methane_handler():
	def generate_data(): 
		while True:
			json_data = json.dumps(
					{'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': methane_val})
			yield f"data:{json_data}\n\n"
			time.sleep(5)
	return Response(stream_with_context(generate_data()), mimetype='text/event-stream')

app.run(host='127.0.0.1', port=8000, debug=True)