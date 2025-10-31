#!/usr/bin/env python3
"""
Script to fetch the latest game configuration data from Idle Clans API
and save it to data/configData.json
"""

import json
import os
from datetime import datetime
from services.api_client import APIClient


def fetch_game_config():
    """Fetch game configuration from API and save to file"""
    print("🔄 Fetching game configuration from Idle Clans API...")

    # Initialize API client
    api_client = APIClient()

    # Fetch game configuration
    try:
        # First, let's try to get the raw response
        import requests
        url = f"{api_client.base_url}/Configuration/game-data"
        print(f"📡 Fetching from: {url}")
        response = requests.get(url)
        print(f"📨 Status Code: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('Content-Type')}")
        print(f"📏 Response Length: {len(response.text)} bytes")
        print(f"🔍 First 200 chars: {response.text[:200]}")

        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            return False

        # Clean MongoDB export format (same as TaskService does)
        import re
        raw_text = response.text
        print("🧹 Cleaning MongoDB export format...")
        # Remove ObjectId() wrapper
        raw_text = re.sub(r'ObjectId\("([^"]+)"\)', r'"\1"', raw_text)
        # Remove _id fields completely
        raw_text = re.sub(r'^\s*"_id":\s*"[^"]*",?\s*\n', '', raw_text, flags=re.MULTILINE)

        # Try to parse as JSON
        config_data = json.loads(raw_text)

        if not config_data:
            print("❌ Failed to fetch configuration data")
            return False

        print(f"✅ Successfully fetched configuration data")

        # Create backup of old config if it exists
        config_path = "data/configData.json"
        if os.path.exists(config_path):
            backup_path = f"data/configData.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            print(f"📦 Creating backup: {backup_path}")
            os.rename(config_path, backup_path)

        # Save new configuration
        print(f"💾 Saving configuration to {config_path}")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

        # Print some stats
        print("\n📊 Configuration Statistics:")
        if 'Items' in config_data and 'Items' in config_data['Items']:
            print(f"  - Items: {len(config_data['Items']['Items'])}")
        if 'Tasks' in config_data:
            print(f"  - Task Categories: {len(config_data['Tasks'])}")
            try:
                total_tasks = sum(
                    len(task['Tasks'][0]['Items'])
                    for task in config_data['Tasks']
                    if isinstance(task, dict) and task.get('Tasks') and len(task['Tasks']) > 0
                )
                print(f"  - Total Tasks: {total_tasks}")
            except Exception as e:
                print(f"  - Total Tasks: (error counting: {e})")

        print("\n✅ Configuration update complete!")
        return True

    except Exception as e:
        print(f"❌ Error fetching configuration: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=== Idle Clans Config Fetcher ===\n")
    success = fetch_game_config()
    exit(0 if success else 1)
