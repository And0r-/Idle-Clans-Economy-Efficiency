import json

# Dev Imports
try:
    from dev import DATA_PATH
except ModuleNotFoundError:
    DATA_PATH = None


def file_to_json(filename):
    with open(filename, "r") as json_file:
        return json.load(json_file)


def fetch_all_items(filepath_to_config_data=DATA_PATH):
    # Path: \AppData\LocalLow\isam_games\Idle Clans\Production\configData.json
    # The configdata file of IC contains all information, we simply fetch on update when needed
    return file_to_json(filepath_to_config_data)


def calculate_max_hit(stat: int, level: int) -> int:
    return int((stat / 8 + level + 13 + stat * level / 64) / 10)


def calculate_augmented_stats(stat: int, level: int) -> int:
    return int((stat + 64) * (level + 8) / 10)


def calculate_hit_chance(
    accuracy: int, level: int, target_defence: int, target_level: int
) -> int:
    ACC = calculate_augmented_stats(accuracy, level)
    DEF = calculate_augmented_stats(target_defence, target_level)
    if ACC < DEF:
        return (ACC - 1) / (2 * DEF)
    return 1 - (DEF + 1) / (2 * ACC)


if __name__ == "__main__":
    STR_STAT = 140
    ACC_STAT = 238
    DEF_STAT = 204
    MAGIC_LVL = 82
    DEF_LVL = 70
    TARGET_STR_STAT = 36
    TARGET_ACC_STAT = 35
    TARGET_DEF_STAT = 36
    TARGET_ACC_LEVEL = 46
    TARGET_STR_LEVEL = 44
    TARGET_DEF_LEVEL = 37
    print("Yours:")
    print(
        f"Hit Chance = {calculate_hit_chance(ACC_STAT, MAGIC_LVL, TARGET_DEF_STAT, TARGET_DEF_LEVEL)}"
    )
    print("Max hit = %s" % calculate_max_hit(STR_STAT, MAGIC_LVL))
    print("Enemy:")
    print(
        f"Hit Chance = {calculate_hit_chance(TARGET_ACC_STAT, TARGET_ACC_LEVEL, DEF_STAT, DEF_LVL)}"
    )
    print("Max hit = %s" % calculate_max_hit(TARGET_STR_STAT, TARGET_ACC_LEVEL))
