runner
======

Script runner based off python and rabbitmq

server
======
Script running service with rest api

The API accepts json data posted to /run_script in the following format:

	{
		"servers":["server1.mydomain.tld","server2.mydomain.tld","server3.mydomain.tld"],
		"script": "#!/bin/bash\nuptime\nwhoami\ndate"
	}

The API should return an ScriptID for you to later check the results of your script run.
The ID json return should look like this:

	{
		"scriptid":1337
	}

You can post the scriptid back to the api to retrieve your results.
Results should be returned as json data as such:

{
	"server1.mydomain.tld":" 18:01:58 up 10 days, 6 min,  8 users,  load average: 0.10, 0.06, 0.11\nkrasmussen\nMon Jan 20 18:01:58 MST 2014\n"
	"server2.mydomain.tld":" 18:01:58 up 10 days, 6 min,  8 users,  load average: 0.10, 0.06, 0.11\nkrasmussen\nMon Jan 20 18:01:58 MST 2014\n"
	"server3.mydomain.tld":" 18:01:58 up 10 days, 6 min,  8 users,  load average: 0.10, 0.06, 0.11\nkrasmussen\nMon Jan 20 18:01:58 MST 2014\n"
}

  Any errors that occur should be returned as such:

	{
		'error':'<some error message>'
	}

client
======
Script that listens for inbound scripts to run via rabbitmq and reports back to the server.

Note: reporting back hasn't been implemented yet but will be soon.
