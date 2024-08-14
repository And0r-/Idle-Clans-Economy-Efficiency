import json

def fileToJson(filename):
    with open(filename, 'r') as json_file:
        return json.load(json_file)