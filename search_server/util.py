import json

def readjson(filename):
    with open(filename, 'rb') as outfile:
        return json.load(outfile)
