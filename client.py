#!/bin/env python
# Import all the things as I'm not sure what out of these I'm going to need yet will clean up imports later
import pika
import socket
import subprocess
import tempfile
import os
import stat
import json

# Will probably setup a config file for rabbit server in the future.

rabbitserver = "localhost"

# going off hostname really is a bad idea and I should set up servers with uniqe ids at some point.
queuename = socket.gethostname()

# Attempt to connect to rabbitmq server or die
try:
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitserver,port=5672))
except:
	print("conection to %s failed" %(rabbitserver))
	os._exit(1)

# Setup channel/queue
channel = connection.channel()
channel.queue_declare(queue=queuename)

# What happens when we get a message
def callback(ch, method, properties, body):
	# Create temp file containing the script
	temp = tempfile.NamedTemporaryFile(delete=False)
	body = json.loads(body)
	temp.write(body['script'])
	temp.close()
	# Make sure the file is executable and fix perms if it isn't
	if not os.access(temp.name, os.X_OK):
		print("%s is not executable attempting to make it executable now" %(temp.name))
		# Not 100% sure how I can make this work across different OSes yet.
		try:
			# May want to change this to using octal as I think it would save me the stat import\
			# but I'm leaving it until I get a chance to test if this works in Windows (doubt it will though).
			os.chmod(temp.name, stat.S_IRUSR | stat.S_IXUSR)
		except Exception as E:
			print("ERROR: Unable to make %s executable. Exiting" %(temp.name))
			print("Exception: %s" %(E))
			# Instead of exiting here I should probably report back a failure in the future
			os.__exit(1)

	# Need to add timeout options so a script can't hang forever

	# Run the script
	process = subprocess.Popen(temp.name)
	process.wait()
	# Need to save this output to a var and pass it back through rabbitmq
	process.communicate()

	# Remove temp file as its no-longer needed
	temp.unlink(temp.name)

	# Need code that kicks the results back to the server through rabbitmq.


# setup how the queue is consumed
channel.basic_consume(callback,queue=queuename,no_ack=True)

# process the queue
print "Waiting for incoming messages..."

try:
	channel.start_consuming()
except (KeyboardInterrupt, SystemExit):
	print("Exiting...")
except:
	raise