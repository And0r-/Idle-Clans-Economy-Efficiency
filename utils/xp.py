import json


class XP:
    def __init__(self, file_path="data/xp_table.json") -> None:
        self.table = []
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
            for lvl in data.values():
                self.table.append(lvl["xp"])

    def xp_to_level(self, xp: float) -> int:
        if xp < 0:
            # todo: Throw Error
            print("INVALID XP:", xp)
            return -1
        num_levels = len(self.table)
        for lvl in range(num_levels):
            if xp < self.table[lvl]:
                return lvl
        return num_levels

    def level_to_xp(self, level: float) -> int:
        if 1 > level or level > len(self.table):
            # todo: Throw Error
            print("INVALID LEVEL:", level)
            return -1
        return self.table[level - 1]
