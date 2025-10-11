import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_babel import Babel, gettext, ngettext, lazy_gettext
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

# i18n Configuration
app.config['LANGUAGES'] = {
    'en': 'English',
    'de': 'Deutsch'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

# Initialize Babel
babel = Babel(app)

# Create translation helper functions
_ = gettext  # Standard gettext function
_l = lazy_gettext  # Lazy gettext for form labels etc.

@babel.localeselector
def get_locale():
    """Select locale based on request"""
    # 1. Check if user explicitly selected a language (future feature)
    # 2. Check browser Accept-Language header
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'en'

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

    # Create tooltip for cost breakdown
    task.cost_tooltip = create_cost_tooltip(task.costs or [], latest_prices)

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


def create_cost_tooltip(costs, latest_prices):
    """Create a tooltip showing cost breakdown"""
    if not costs:
        return _("No materials required")

    tooltip_lines = [_("Material Costs:")]

    for cost in costs:
        if cost.item:
            cost_item_price = latest_prices_get_item(latest_prices, cost.item.id)
            # Translate item name (for now just use key, later we'll add translations)
            item_name = translate_item_name(cost.item.name)

            if cost_item_price:
                unit_price = cost_item_price["lowestSellPrice"]
                total_cost = unit_price * cost.amount
                tooltip_lines.append(f"• {item_name}: {cost.amount}x @ {unit_price:.2f} = {total_cost:.2f} gold")
            else:
                # Fallback to base value
                unit_price = cost.item.base_value
                total_cost = unit_price * cost.amount
                tooltip_lines.append(f"• {item_name}: {cost.amount}x @ {unit_price:.2f} (base) = {total_cost:.2f} gold")

    return "\n".join(tooltip_lines)


def translate_item_name(item_key):
    """Translate item name - for now return key, later add proper translations"""
    # TODO: Add item name translations here
    # This will be where we map API keys to localized names
    return item_key  # For now, just return the key


def translate_category_name(category_key):
    """Translate category name - for now return key, later add proper translations"""
    # TODO: Add category name translations here
    return category_key  # For now, just return the key


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
                    'name': translate_category_name(category.name),
                    'raw_name': category.name,  # Keep original for debugging
                    'tasks_with_data': []
                }

                for task in category.tasks:
                    if calculateEfficiency(task, verbose=False):
                        task.category_name = translate_category_name(category.name)
                        # Add translated names for display
                        task.display_name = translate_item_name(task.name)
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
            return f"<h1>{_('Loading data... Please refresh in a moment.')}</h1>"

    with data_lock:
        data_copy = cached_data.copy() if cached_data else {}

    # Make translation functions available in template
    data_copy['_'] = _
    data_copy['translate_item_name'] = translate_item_name
    data_copy['translate_category_name'] = translate_category_name

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
        print("🌐 Starting production WSGI server (Waitress)...")
        print("📊 Open your browser to: http://localhost:5000")
        print("🔄 Data updates automatically every 15 minutes")
        print("🔒 Production-ready server running")

        # Use Waitress for production - secure and works with background tasks
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000, threads=4)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        if scheduler:
            scheduler.shutdown()
        print("✅ Scheduler stopped")