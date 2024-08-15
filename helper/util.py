import json

# Dev Imports
try:
    from dev import DATA_PATH
except ModuleNotFoundError:
    DATAPATH = None


def file_to_json(filename):
    with open(filename, "r") as json_file:
        return json.load(json_file)


def fetch_all_items(filepath_to_config_data=DATA_PATH):
    # Path: \AppData\LocalLow\isam_games\Idle Clans\Production\configData.json
    # The configdata file of IC contains all information, we simply fetch on update when needed
    return file_to_json(filepath_to_config_data)
