import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
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

# Initialize Flask app
app = Flask(__name__)

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
cached_data = None
last_update = None
data_lock = threading.Lock()
scheduler = None


def fetchPrices():
    global latest_prices
    latest_prices = player_market_service.get_items_prices_latest(
        include_average_price=True
    )


def calculateEfficiency(task, character={"xp_multiplier": 1, "time_multiplier": 1}, verbose=True):
    # Todo: Calculate effective time from time multiplier
    # effective_time = character["time_multiplier"] * task.base_time
    # Convert from milliseconds to seconds
    effective_time = task.base_time / 1000.0

    # Skip tasks with invalid data
    if task.item_reward is None:
        if verbose:
            print(f"Skipping task '{task.name}' - no item reward")
        return False

    if effective_time <= 0:
        if verbose:
            print(f"Skipping task '{task.name}' - invalid base time: {effective_time}")
        return False

    # Calculate xp/time
    task.xp_efficiency = character["xp_multiplier"] * task.exp_reward / effective_time
    task.gold_efficiency_calculation_time = time.time()

    # Calculate profit (revenue - costs) / time
    if latest_prices == None:
        if verbose:
            print("Latest market prices are unavailable for gold calculation")
        return False

    # Calculate revenue
    item_price = latest_prices_get_item(latest_prices, task.item_reward.id)
    if not item_price:
        if verbose:
            print(f"  No market data for {task.item_reward.id}")
        return False

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

    if verbose:
        # Print efficiency results for this task
        print(f"Task: {task.name}")
        print(f"  Revenue: {task.revenue:.2f} gold ({task.item_amount}x items)")
        print(f"  Costs: {task.total_cost:.2f} gold (materials)")
        print(f"  Net Profit: {task.net_profit:.2f} gold")
        print(f"  Time: {effective_time:.0f}s")
        print(f"  Profit/sec: {task.gold_efficiency:.3f} gold/sec")
        print(f"  XP/sec: {task.xp_efficiency:.2f}")
        print()

    return True


def latest_prices_get_item(latest_prices, id):
    for item in latest_prices:
        if item["itemId"] == id:
            return item


def load_and_calculate_data():
    """Load market data and calculate efficiency for all tasks - Background job"""
    global cached_data, last_update

    try:
        with data_lock:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Fetching market prices...")
            fetchPrices()

            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Analyzing {len(task_service.categories)} categories...")

            # Calculate efficiency for all tasks
            categories_data = []
            all_tasks = []

            for category in task_service.categories:
                category_data = {
                    'name': category.name,
                    'tasks_with_data': []
                }

                for task in category.tasks:
                    if calculateEfficiency(task, verbose=False):
                        task.category_name = category.name  # Add category name to task
                        category_data['tasks_with_data'].append(task)
                        all_tasks.append(task)

                # Sort tasks by profit efficiency
                category_data['tasks_with_data'].sort(key=lambda t: t.gold_efficiency, reverse=True)
                categories_data.append(category_data)

            # Sort all tasks by profit efficiency
            all_tasks.sort(key=lambda t: t.gold_efficiency, reverse=True)

            cached_data = {
                'categories': categories_data,
                'all_tasks': all_tasks,
                'total_categories': len(task_service.categories),
                'total_tasks': sum(len(cat['tasks_with_data']) for cat in categories_data),
                'profitable_tasks': len([t for t in all_tasks if t.gold_efficiency > 0]),
                'top_tasks': all_tasks[:10],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            last_update = time.time()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Data loading complete! Next update in 15 minutes.")

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error updating data: {e}")

    return cached_data


@app.route('/')
def index():
    global cached_data

    # Wait for initial data if not loaded yet
    if not cached_data:
        print("⏳ Waiting for initial data load...")
        time.sleep(2)  # Give scheduler time to load data
        if not cached_data:
            return "<h1>🔄 Loading data... Please refresh in a moment.</h1>"

    with data_lock:
        data_copy = cached_data.copy() if cached_data else {}

    return render_template('index.html', **data_copy)


@app.route('/refresh')
def refresh():
    """Just refresh the frontend view - no new API calls"""
    return index()




@app.route('/status')
def status():
    """API endpoint to check data freshness"""
    global last_update, cached_data

    return jsonify({
        'last_update': datetime.fromtimestamp(last_update).strftime('%Y-%m-%d %H:%M:%S') if last_update else None,
        'data_loaded': bool(cached_data),
        'minutes_since_update': int((time.time() - last_update) / 60) if last_update else None
    })


def start_scheduler():
    """Start background scheduler for periodic data updates"""
    global scheduler

    scheduler = BackgroundScheduler()
    # Load data immediately on startup
    load_and_calculate_data()
    # Then schedule updates every 15 minutes
    scheduler.add_job(
        func=load_and_calculate_data,
        trigger="interval",
        minutes=15,
        id='update_market_data'
    )
    scheduler.start()
    print("📅 Background scheduler started - updating data every 15 minutes")


if __name__ == "__main__":
    print("=== 🏆 Idle Clans Profit Optimizer - Web Server ===")
    print("🚀 Starting background data scheduler...")
    start_scheduler()

    try:
        print("🌐 Starting web server...")
        print("📊 Open your browser to: http://localhost:5000")
        print("🔄 Data updates automatically every 15 minutes")
        app.run(debug=False, host='0.0.0.0', port=5000)  # debug=False for production
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        if scheduler:
            scheduler.shutdown()
        print("✅ Scheduler stopped")