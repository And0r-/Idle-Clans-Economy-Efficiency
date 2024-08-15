import json


def fileToJson(filename):
    with open(filename, "r") as json_file:
        return json.load(json_file)


def getAllItems(filepathToConfigData):
    # Path: \AppData\LocalLow\isam_games\Idle Clans\Production\configData.json
    pass
