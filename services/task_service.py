import json

from services import ItemService
from services.item_service import Item


class TaskService:
    def __init__(self, item_service: ItemService, file_path="data/configData.json"):
        self.categories: list[TaskCategory] = []

        with open(file_path, "r") as json_file:
            raw_text = json_file.read()
            # Clean MongoDB export format
            import re
            # Remove ObjectId() wrapper
            raw_text = re.sub(r'ObjectId\("([^"]+)"\)', r'"\1"', raw_text)
            # Remove _id fields completely
            raw_text = re.sub(r'^\s*"_id":\s*"[^"]*",?\s*\n', '', raw_text, flags=re.MULTILINE)
            data = json.loads(raw_text)

            self.categories = [
                TaskCategory(
                    id=task["Tasks"][0]["Items"][0]["TaskId"],
                    skill_id=task["Tasks"][0]["Items"][0]["Skill"],
                    name=task["Key"],
                    tasks=[
                        TaskItem(
                            name=task_item["Name"],
                            item_reward=(
                                item_service.get_item_by_id(task_item["ItemReward"])
                                if task_item["ItemReward"] != -1
                                else None
                            ),
                            level_requirement=task_item["LevelRequirement"],
                            base_time=task_item["BaseTime"],
                            exp_reward=task_item["ExpReward"],
                            item_amount=task_item["ItemAmount"],
                            costs=[
                                TaskCost(
                                    item=item_service.get_item_by_id(cost["Item"]),
                                    amount=cost["Amount"],
                                )
                                for cost in task_item["Costs"] or []
                            ],
                        )
                        for task_item in task["Tasks"][0]["Items"]
                    ],
                )
                for task in data["Tasks"]
            ]

    def get_tasks(self):
        return self.categories


class TaskCost:
    def __init__(
        self,
        item: Item,
        amount: int,
    ) -> None:
        self.item = item
        self.amount = amount


class TaskItem:
    def __init__(
        self,
        name: str = None,
        item_reward: Item = None,
        level_requirement: float = None,
        base_time: float = None,
        exp_reward: float = None,
        item_amount: int = None,
        costs=None,
    ) -> None:
        self.name = name
        self.item_reward = item_reward
        self.level_requirement = level_requirement
        self.base_time = base_time
        self.exp_reward = exp_reward
        self.item_amount = item_amount
        self.costs = costs
        self.gold_efficiency = None
        self.xp_efficiency = None
        self.gold_efficiency_calculation_time = None
        self.xp_efficiency_calculation_time = None
        self.sold_as_base_price = False


class TaskCategory:
    def __init__(
        self,
        id: int = None,
        skill_id: int = None,
        name="",
        tasks: list[TaskItem] = [],
    ) -> None:
        self.id = id
        self.skill_id = skill_id
        self.name = name
        self.tasks = tasks
