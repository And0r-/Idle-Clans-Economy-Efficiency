import json
import time
from services import (
    APIClient,
    ChatService,
    ClanService,
    LeaderboardService,
    PlayerService,
    PlayerMarketService,
)
from helper import AsciiUI, file_to_json

# Dev Imports
try:
    from dev import NAME
except ModuleNotFoundError:
    NAME = None


# Initialize API Client
api_client = APIClient()
# Initialize DataServices
chat_service = ChatService(api_client)
clan_service = ClanService(api_client)
leaderboard_service = LeaderboardService(api_client)
player_service = PlayerService(api_client)
player_market_service = PlayerMarketService(api_client)
ascii_ui = AsciiUI()

lastPriceFetch = None
priceFetchIntervalLimit = 10


def fetchPrices():
    global latest_prices
    global lastPriceFetch
    if lastPriceFetch and time.time() - lastPriceFetch < priceFetchIntervalLimit:
        return print(
            f"Price fetched no more than {priceFetchIntervalLimit} seconds ago. \nTry again later."
        )
    try:
        latest_prices = file_to_json("dev/item_prices_latest.json")
    except:
        latest_prices = player_market_service.get_items_prices_latest()
    lastPriceFetch = time.time()
    print("Market price fetched!")


def calculateEfficiency():
    global latest_prices
    if time.time() - lastPriceFetch > priceFetchIntervalLimit:
        fetchPrices()
    latest_prices.sort(reverse=True, key=lambda item: item["lowestSellPrice"])
    print(json.dumps(latest_prices[:10], indent=4))


if __name__ == "__main__":

    # latest_prices = player_market_service.get_items_prices_latest()
    fetchPrices()

    menuSelection = -1
    while menuSelection != "0":
        print("TEMP: MAIN: MENU SELECTION")
        menuSelection = ascii_ui.menu()
        if menuSelection == "1":
            ascii_ui.calculate_gold_efficiency()
        elif menuSelection == "2":
            ascii_ui.market_search()
        elif menuSelection == "3":
            ascii_ui.reload_data()
        elif menuSelection == "4":
            ascii_ui.settings()
        elif menuSelection == "-1":
            print("TEMP:")
            print(
                json.dumps(
                    player_market_service.get_items_prices_history(158),
                    # player_service.get_profile("TheMucker"),
                    indent=4,
                )
            )
    print("\nThank you for using Idle Clans Profit Calculator")
