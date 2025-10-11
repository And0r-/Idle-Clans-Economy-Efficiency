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

    # Skip tasks with invalid data
    if task.item_reward is None:
        print(f"Skipping task '{task.name}' - no item reward")
        return

    if effective_time <= 0:
        print(f"Skipping task '{task.name}' - invalid base time: {effective_time}")
        return

    # Calculate xp/time
    task.xp_efficiency = character["xp_multiplier"] * task.exp_reward / effective_time
    task.gold_efficiency_calculation_time = time.time()

    # Calculate profit (revenue - costs) / time
    if latest_prices == None:
        return print("Latest market prices are unavailable for gold calculation")

    # Calculate revenue
    item_price = latest_prices_get_item(latest_prices, task.item_reward.id)
    if not item_price:
        print(f"  No market data for {task.item_reward.id}")
        return

    revenue = max(
        task.item_reward.base_value * task.item_amount,
        item_price["highestBuyPrice"] * task.item_amount
    )
    task.sold_as_base_price = task.item_reward.base_value >= item_price["highestBuyPrice"]

    # Calculate material costs
    total_cost = 0
    for cost in task.costs or []:
        if cost.item:
            cost_item_price = latest_prices_get_item(latest_prices, cost.item.id)
            if cost_item_price:
                # Use lowest sell price (what we'd pay to buy materials)
                material_cost = cost_item_price["lowestSellPrice"] * cost.amount
                total_cost += material_cost
            else:
                # Fallback to base value if no market data
                total_cost += cost.item.base_value * cost.amount

    # Calculate net profit and efficiency
    net_profit = revenue - total_cost
    task.gold_efficiency = net_profit / effective_time
    task.total_cost = total_cost
    task.revenue = revenue
    task.net_profit = net_profit
    task.xp_efficiency_calculation_time = time.time()

    # Print efficiency results for this task
    print(f"Task: {task.name}")
    print(f"  Revenue: {task.revenue:.2f} gold ({task.item_amount}x items)")
    print(f"  Costs: {task.total_cost:.2f} gold (materials)")
    print(f"  Net Profit: {task.net_profit:.2f} gold")
    print(f"  Time: {effective_time:.0f}s")
    print(f"  Profit/sec: {task.gold_efficiency:.3f} gold/sec")
    print(f"  XP/sec: {task.xp_efficiency:.2f}")
    print()


def latest_prices_get_item(latest_prices, id):
    for item in latest_prices:
        if item["itemId"] == id:
            return item


if __name__ == "__main__":
    print("=== Idle Clans Profit Optimizer ===")
    print("Fetching market prices...")
    fetchPrices()

    print(f"Analyzing {len(task_service.categories)} categories...")
    print()

    # Calculate efficiency for all tasks
    all_tasks = []
    for category in task_service.categories:
        print(f"Category: {category.name}")
        for task in category.tasks:
            calculateEfficiency(task)
            if hasattr(task, 'gold_efficiency') and task.gold_efficiency:
                all_tasks.append(task)

    # Show top 10 most profitable tasks
    if all_tasks:
        print("=" * 50)
        print("TOP 10 MOST PROFITABLE TASKS:")
        print("=" * 50)
        all_tasks.sort(key=lambda t: t.gold_efficiency, reverse=True)
        for i, task in enumerate(all_tasks[:10], 1):
            print(f"{i:2}. {task.name}")
            print(f"    Gold/sec: {task.gold_efficiency:.2f}")
            print(f"    XP/sec: {task.xp_efficiency:.2f}")
            print()

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
