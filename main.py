import json
import time
from services import (
    APIClient,
    ChatService,
    ClanService,
    LeaderboardService,
    PlayerService,
    PlayerMarketService,
    ItemService,
    TaskService,
)
from utils import AsciiUI


# Initialize API Client
api_client = APIClient()
# Initialize API DataServices
chat_service = ChatService(api_client)
clan_service = ClanService(api_client)
leaderboard_service = LeaderboardService(api_client)
player_service = PlayerService(api_client)
player_market_service = PlayerMarketService(api_client)
# Initialize local DataServices
item_service = ItemService()
task_service = TaskService(item_service)
ascii_ui = AsciiUI()

latest_prices = None
character = None


def fetchPrices():
    global latest_prices
    latest_prices = player_market_service.get_items_prices_latest(
        include_average_price=True
    )


def calculateEfficiency(task, character={"xp_multiplier": 1, "time_multiplier": 1}):
    # Todo: Calculate effective time from time multiplier
    # effective_time = character["time_multiplier"] * task.base_time
    effective_time = task.base_time
    # Calculate xp/time
    task.xp_efficiency = character["xp_multiplier"] * task.exp_reward / effective_time
    task.gold_efficiency_calculation_time = time.time()

    # Cauculate gold/time
    if latest_prices == None:
        return print("Latest market prices are unavailable for gold calculation")
    base_gold_efficiency = task.item_reward.base_value / effective_time
    market_gold_efficiency = (
        latest_prices_get_item(latest_prices, task.item_reward.id)["highestBuyPrice"]
        / effective_time
    )
    if base_gold_efficiency >= market_gold_efficiency:
        task.gold_efficiency = base_gold_efficiency
        task.sold_as_base_price = True
    else:
        task.gold_efficiency = market_gold_efficiency
    task.xp_efficiency_calculation_time = time.time()
    latest_prices.sort(reverse=True, key=lambda item: item["lowestSellPrice"])
    print(json.dumps(latest_prices[:10], indent=4))


def latest_prices_get_item(latest_prices, id):
    for item in latest_prices:
        if item["itemId"] == id:
            return item


if __name__ == "__main__":
    print("PROGRAM START")
    fetchPrices()
    for category in task_service.categories:
        for task in category.tasks:
            calculateEfficiency(task)

    # menuSelection = -1
    # while menuSelection != "0":
    #     print(ascii_ui.menu())
    #     usr = input("Please choose an option: ")
    #     while usr < "0" or usr > str(4):
    #         usr = input("Please choose an option: ")
    #     if menuSelection == "1":
    #         print(ascii_ui.calculate_gold_efficiency())
    #     elif menuSelection == "2":
    #         print(ascii_ui.market_search())
    #     elif menuSelection == "3":
    #         print(ascii_ui.reload_data())
    #     elif menuSelection == "4":
    #         print(ascii_ui.settings())
    #     elif menuSelection == "-1":
    #         print("TEMP:")
    #         print(
    #             json.dumps(
    #                 player_market_service.get_items_prices_history(158),
    #                 # player_service.get_profile("TheMucker"),
    #                 indent=4,
    #             )
    #         )
    print("\nThank you for using Idle Clans Profit Calculator")
