import json


class ItemService:
    def __init__(self, file_path="data/configData.json"):
        self.data: list[Item] = []
        with open(file_path, "r") as json_file:
            raw_text = json_file.read()
            # Clean MongoDB export format (same as TaskService)
            import re
            # Remove ObjectId() wrapper
            raw_text = re.sub(r'ObjectId\("([^"]+)"\)', r'"\1"', raw_text)
            # Remove _id fields completely
            raw_text = re.sub(r'^\s*"_id":\s*"[^"]*",?\s*\n', '', raw_text, flags=re.MULTILINE)
            data = json.loads(raw_text)
            for item in data["Items"]["Items"]:
                if (
                    not item["CanNotBeTraded"]
                    and not item["Discontinued"]
                    and not item["CanNotBeSoldToGameShop"]
                ):
                    self.data.append(
                        Item(
                            item["ItemId"],
                            item["Name"],
                            item["BaseValue"],
                            item["AssociatedSkill"],
                        )
                    )

    def get_item_by_id(self, id):
        for item in self.data:
            if item.id == id:
                return item


class Item(object):
    def __init__(
        self,
        id,
        name,
        base_value,
        associated_skill,
    ) -> None:
        self.id = id
        self.name = name
        self.base_value = base_value
        self.associated_skill = associated_skill


if __name__ == "__main__":
    item_service = ItemService()
    for item in item_service.data:
        if item.base_value < 10:
            print(item.name, item.base_value)
