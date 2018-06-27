import os
import json

def unknownJsonSiteLog(obj, filename):
	try:
		os.mkdir('./unknownsites')
	except Exception as e:
		pass
	filename = './unknownsites/'+filename
	with open(filename, 'w') as f:
		f.write(json.dumps(obj))

def writeParseJson(jsonKey, jsonDict):
	try:
		os.mkdir('./jsonfiles')
	except Exception as e:
		pass
	filename = './jsonfiles/'+str(jsonKey)+'.json'
	with open(filename, 'w') as f:
		f.write(json.dumps(jsonDict))

def readParseJson(jsonKey):
	if (not os.path.isdir('./jsonfiles')):
		return None
	filename = './jsonfiles/'+str(jsonKey)+'.json'
	if (not os.path.isfile(filename)):
		return None
	with open(filename, 'r') as f:
		return json.loads(f.read())