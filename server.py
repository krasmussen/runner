#!/bin/env python

# This script is to provide a script running service with a rest api
# The API accepts json data posted to /run_script in the following format:

#	{
#		"servers":["server1.mydomain.tld","server2.mydomain.tld","server3.mydomain.tld"],
#		"script": "#!/bin/bash\nuptime\nwhoami\ndate"
#	}

# The API should return an ScriptID for you to later check the results of your script run.
# The ID json return should look like this:

#	{
#		"scriptid":1337
#	}

# You can post the scriptid back to the api to retrieve your results.
# Results should be returned as json data as such:

#{
#	"server1.mydomain.tld":" 18:01:58 up 10 days, 6 min,  8 users,  load average: 0.10, 0.06, 0.11\nkrasmussen\nMon Jan 20 18:01:58 MST 2014\n"
#	"server2.mydomain.tld":" 18:01:58 up 10 days, 6 min,  8 users,  load average: 0.10, 0.06, 0.11\nkrasmussen\nMon Jan 20 18:01:58 MST 2014\n"
#	"server3.mydomain.tld":" 18:01:58 up 10 days, 6 min,  8 users,  load average: 0.10, 0.06, 0.11\nkrasmussen\nMon Jan 20 18:01:58 MST 2014\n"
#}

# Any errors that occur should be returned as such:

#	{
#		'error':'<some error message>'
#	}

import pika
import json
from flask import Flask, request, abort, make_response

# Will probably setup a config file for rabbit server in the future.
rabbitserver = "localhost"

# Attempt to connect to rabbitmq server or die
try:
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitserver,port=5672))
except:
	print("conection to %s failed" %(rabbitserver))
	os._exit(1)

# Setup channel
channel = connection.channel()

# make sure needed queue is setup and send message to said queue
def sendmessage(message,queuename):
	channel.queue_declare(queue="%s" %(queuename))
	channel.basic_publish(exchange='',routing_key='%s' %(queuename),body="%s" %(message))

# Setup flask app
app = Flask(__name__)


# Setup json responses for http errors
@app.errorhandler(400)
def bad_request(error):
	return make_response(json.dumps({'error':'Bad Request'}), 400)

@app.errorhandler(404)
def not_found(error):
	return make_response(json.dumps({'error':'Not Found'}), 404)

@app.errorhandler(500)
def server_error(error):
	return make_response(json.dumps({'error':'Internal Server Error'}), 500)

# Setup run_script api call
@app.route('/run_script', methods=['GET','POST'])
def run_script_api():
	# Make sure data sent to us is json and contains the correct data
	if not request.json:
		abort(400)
	if 'servers' in request.json and type(request.json['servers']) is not list:
		abort(400)
	if 'script' in request.json and type(request.json['script']) is not unicode:
		abort(400)

	msg = json.dumps({"msgid":str(5),"script":request.json['script']})

	for server in request.json.get('servers'):
		print("message: %s\n\n\nserver: %s\n" %(msg,server))
		sendmessage(msg,str(server))

	return(json.dumps({"scriptid":str(5)}))


# Need api call to take an id and return the results of the previous script run


# Run flask app
if __name__ == '__main__':
	app.run(debug = True)