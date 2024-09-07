# import json
# def fetch_all_items(filepath_to_config_data=DATA_PATH):
#     # Path: \AppData\LocalLow\isam_games\Idle Clans\Production\configData.json
#     # The configdata file of IC contains all information, we simply fetch on update when needed
#     with open(filepath_to_config_data, "r") as json_file:
#         return json.load(json_file)


def calculate_max_hit(stat: int, level: int, weakness_match: bool = False) -> int:
    if weakness_match:
        return int((stat / 8 + level + 13 + stat * level / 64) / 10 * 1.2)
    return int((stat / 8 + level + 13 + stat * level / 64) / 10)


def calculate_augmented_stats(stat: int, level: int) -> int:
    return int((stat + 64) * (level + 8) / 10)


def calculate_hit_chance(
    accuracy: int,
    level: int,
    target_defence: int,
    target_level: int,
    weakness_match: bool = False,
) -> int:
    ACC = calculate_augmented_stats(accuracy, level)
    DEF = calculate_augmented_stats(target_defence, target_level)
    if weakness_match:
        DEF *= 0.8

    if ACC < DEF:
        return int(((ACC - 1) / (2 * DEF)) * 100)
    return int((1 - (DEF + 1) / (2 * ACC)) * 100)


if __name__ == "__main__":
    STR_STAT = 71 + 14
    ACC_STAT = 76
    DEF_STAT = 221
    STR_LVL = 69
    ACC_LVL = 55
    DEF_LVL = 58
    weakness_match = True
    TARGET_STR_STAT = 0
    TARGET_ACC_STAT = 0
    TARGET_DEF_STAT = 0
    TARGET_STR_LEVEL = 0
    TARGET_ACC_LEVEL = 0
    TARGET_DEF_LEVEL = 0
    print("Yours:")
    print(
        f"Hit Chance = {calculate_hit_chance(ACC_STAT, ACC_LVL, TARGET_DEF_STAT, TARGET_DEF_LEVEL, weakness_match)}"
    )
    print("Max hit = %s" % calculate_max_hit(STR_STAT, STR_LVL, weakness_match))
    print("Enemy:")
    print(
        f"Hit Chance = {calculate_hit_chance(TARGET_ACC_STAT, TARGET_ACC_LEVEL, DEF_STAT, DEF_LVL)}"
    )
    print("Max hit = %s" % calculate_max_hit(TARGET_STR_STAT, TARGET_ACC_LEVEL))
