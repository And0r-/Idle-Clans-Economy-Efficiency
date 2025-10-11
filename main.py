import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request, make_response
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
babel = Babel()

def get_locale():
    """Select locale based on request"""
    try:
        # 1. Check if user explicitly selected a language via cookie
        if request and hasattr(request, 'cookies') and 'language' in request.cookies:
            lang = request.cookies.get('language')
            if lang in app.config['LANGUAGES']:
                return lang
    except RuntimeError:
        # Handle case when called outside request context (e.g., background scheduler)
        pass

    # 2. Default to English
    return 'en'

# Initialize Babel with app and locale selector
babel.init_app(app, locale_selector=get_locale)

# Create translation helper functions
_ = gettext  # Standard gettext function
_l = lazy_gettext  # Lazy gettext for form labels etc.

# Dynamic translation collection
missing_translations = {
    'items': set(),
    'categories': set()
}

# Translation maps - loaded from JSON files
ITEM_TRANSLATIONS = {}
CATEGORY_TRANSLATIONS = {}

def load_translations():
    """Load translations from JSON files"""
    global ITEM_TRANSLATIONS, CATEGORY_TRANSLATIONS

    for locale in ['en', 'de']:
        try:
            with open(f'translations/{locale}.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                ITEM_TRANSLATIONS[locale] = data.get('items', {})
                CATEGORY_TRANSLATIONS[locale] = data.get('categories', {})
        except FileNotFoundError:
            print(f"Warning: Translation file translations/{locale}.json not found")
            ITEM_TRANSLATIONS[locale] = {}
            CATEGORY_TRANSLATIONS[locale] = {}
        except Exception as e:
            print(f"Error loading translations for {locale}: {e}")
            ITEM_TRANSLATIONS[locale] = {}
            CATEGORY_TRANSLATIONS[locale] = {}

# Load translations
load_translations()

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
    # Get prices with average price (24h) included
    latest_prices = player_market_service.get_items_prices_latest(
        include_average_price=True
    )


def calculateEfficiency(task, character={"xp_multiplier": 1, "time_multiplier": 1}, verbose=True, collect_missing=False):
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
    item_price_data = latest_prices_get_item(latest_prices, task.item_reward.id)
    if not item_price_data:
        if verbose:
            print(f"  No market data for {task.item_reward.id}")
        return False

    # Use new price function for selling
    sell_price = get_item_price(item_price_data, price_type='sell')
    if not sell_price or sell_price <= 0:
        sell_price = task.item_reward.base_value  # Fallback to base value

    revenue = max(
        task.item_reward.base_value * task.item_amount,
        sell_price * task.item_amount
    )
    task.sold_as_base_price = task.item_reward.base_value >= sell_price

    # Calculate material costs
    total_cost = 0
    for cost in task.costs or []:
        if cost.item:
            cost_item_price_data = latest_prices_get_item(latest_prices, cost.item.id)
            if cost_item_price_data:
                # Use new price function for buying materials
                buy_price = get_item_price(cost_item_price_data, price_type='buy')
                if buy_price and buy_price > 0:
                    material_cost = buy_price * cost.amount
                    total_cost += material_cost
                else:
                    # Fallback to base value if no valid price
                    total_cost += cost.item.base_value * cost.amount
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
    task.cost_tooltip = create_cost_tooltip(task.costs or [], latest_prices, collect_missing)

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

# Price strategy configuration (can be made configurable later)
PRICE_STRATEGY = {
    'sell': 'average_1d',  # Options: 'instant', 'average_1d', 'average_7d', 'average_30d'
    'buy': 'instant'       # Options: 'instant', 'average_1d', 'average_7d', 'average_30d'
}

def get_item_price(item_price_data, price_type='sell'):
    """
    Get the price for an item based on configured strategy

    Args:
        item_price_data: Price data from API for a specific item
        price_type: 'sell' for revenue calculation, 'buy' for cost calculation

    Returns:
        float: The price to use for calculations
    """
    if not item_price_data:
        return None

    strategy = PRICE_STRATEGY.get(price_type, 'average_1d')

    if strategy == 'instant':
        if price_type == 'sell':
            # Instant sell: what buyers are offering right now
            return item_price_data.get("highestBuyPrice", 0)
        else:
            # Instant buy: what sellers are asking right now
            return item_price_data.get("lowestSellPrice", 0)

    elif strategy == 'average_1d':
        # Use 24h average price (more stable, realistic)
        avg_price = item_price_data.get("averagePrice", None)
        if avg_price:
            return avg_price
        # Fallback to instant if no average available
        return get_item_price(item_price_data, price_type='sell' if price_type == 'sell' else 'buy')

    # For now, other strategies fallback to 1d average
    # TODO: Implement 7d and 30d averages when we fetch comprehensive data
    return get_item_price(item_price_data, price_type)


def create_cost_tooltip(costs, latest_prices, collect_missing=False):
    """Create a tooltip showing cost breakdown"""
    if not costs:
        return _("No materials required")

    tooltip_lines = [_("Material Costs:")]

    for cost in costs:
        if cost.item:
            cost_item_price_data = latest_prices_get_item(latest_prices, cost.item.id)
            # Translate item name (for now just use key, later we'll add translations)
            item_name = translate_item_name(cost.item.name, collect_missing)

            if cost_item_price_data:
                unit_price = get_item_price(cost_item_price_data, price_type='buy')
                if unit_price and unit_price > 0:
                    total_cost = unit_price * cost.amount
                    # Show price source in tooltip
                    price_type = "(avg)" if PRICE_STRATEGY['buy'] == 'average_1d' else ""
                    tooltip_lines.append(f"• {item_name}: {cost.amount}x @ {unit_price:.2f} {price_type} = {total_cost:.2f} gold")
                else:
                    # Fallback to base value
                    unit_price = cost.item.base_value
                    total_cost = unit_price * cost.amount
                    tooltip_lines.append(f"• {item_name}: {cost.amount}x @ {unit_price:.2f} (base) = {total_cost:.2f} gold")
            else:
                # Fallback to base value
                unit_price = cost.item.base_value
                total_cost = unit_price * cost.amount
                tooltip_lines.append(f"• {item_name}: {cost.amount}x @ {unit_price:.2f} (base) = {total_cost:.2f} gold")

    return "\n".join(tooltip_lines)


def translate_item_name(item_key, collect_missing=False):
    """Translate item name with optional collection of missing translations"""
    global missing_translations

    locale = get_locale()
    translations = ITEM_TRANSLATIONS.get(locale, {})

    if item_key in translations:
        return translations[item_key]

    # Collect missing translation only when requested
    if collect_missing:
        missing_translations['items'].add(item_key)

    # Return key for now
    return item_key


def translate_category_name(category_key, collect_missing=False):
    """Translate category name with optional collection of missing translations"""
    global missing_translations

    locale = get_locale()
    translations = CATEGORY_TRANSLATIONS.get(locale, {})

    if category_key in translations:
        return translations[category_key]

    # Collect missing translation only when requested
    if collect_missing:
        missing_translations['categories'].add(category_key)

    # Return key for now
    return category_key


def load_and_calculate_data(collect_missing_translations=False):
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
                # Use English for background job, avoid translation calls that need request context
                category_data = {
                    'name': category.name,  # Use raw name for background job
                    'raw_name': category.name,  # Keep original for debugging
                    'tasks_with_data': []
                }

                for task in category.tasks:
                    if calculateEfficiency(task, verbose=False, collect_missing=collect_missing_translations):
                        task.category_name = category.name  # Use raw name for background job
                        # Use raw name for background job
                        task.display_name = task.name
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

    # Check if user wants to collect missing translations
    collect_missing = request.args.get('i18n') == 'missing'

    # If collecting translations, regenerate data with collection enabled
    if collect_missing:
        print("🔍 Collecting missing translations...")
        load_and_calculate_data(collect_missing_translations=True)

    # Wait for initial data if not loaded yet
    if not cached_data:
        print("⏳ Waiting for initial data load...")
        time.sleep(2)  # Give scheduler time to load data
        if not cached_data:
            return f"<h1>{_('Loading data... Please refresh in a moment.')}</h1>"

    with data_lock:
        data_copy = cached_data.copy() if cached_data else {}

    # Apply translations to the data copy for current user's language
    if data_copy and 'categories' in data_copy:
        for category in data_copy['categories']:
            # Translate category name for current user
            category['name'] = translate_category_name(category['raw_name'], collect_missing)

            # Translate task names for current user
            for task in category['tasks_with_data']:
                task.display_name = translate_item_name(task.name, collect_missing)
                task.category_name = translate_category_name(category['raw_name'], collect_missing)

    # Make translation functions available in template
    data_copy['_'] = _
    data_copy['translate_item_name'] = lambda key: translate_item_name(key, collect_missing)
    data_copy['translate_category_name'] = lambda key: translate_category_name(key, collect_missing)

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

@app.route('/translations-needed')
def translations_needed():
    """Debug endpoint showing missing translations"""
    global missing_translations

    return jsonify({
        'missing_items': sorted(list(missing_translations['items'])),
        'missing_categories': sorted(list(missing_translations['categories'])),
        'total_missing_items': len(missing_translations['items']),
        'total_missing_categories': len(missing_translations['categories']),
        'current_locale': get_locale(),
        'example_item_template': {
            item: f"# TODO: Translate '{item}'" for item in list(missing_translations['items'])[:5]
        },
        'example_category_template': {
            cat: f"# TODO: Translate '{cat}'" for cat in list(missing_translations['categories'])[:5]
        }
    })

@app.route('/export-missing-translations')
def export_missing_translations():
    """Export missing translations as JSON for easy copy-paste"""
    global missing_translations

    export_data = {
        "instructions": "Copy these into your translation files",
        "items_to_add": {},
        "categories_to_add": {}
    }

    # Add missing items with placeholder translations
    for item in sorted(missing_translations['items']):
        export_data["items_to_add"][item] = f"TODO: Translate '{item}'"

    # Add missing categories with placeholder translations
    for category in sorted(missing_translations['categories']):
        export_data["categories_to_add"][category] = f"TODO: Translate '{category}'"

    return jsonify(export_data)

@app.route('/set-language/<language>')
def set_language(language):
    """Set user language preference via cookie"""
    if language not in app.config['LANGUAGES']:
        return jsonify({'error': 'Language not supported'}), 400

    response = make_response(jsonify({'status': 'success', 'language': language}))
    # Set cookie for 1 year
    response.set_cookie('language', language, max_age=60*60*24*365)
    return response


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