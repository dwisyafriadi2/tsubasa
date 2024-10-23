import time
import requests

def get_init_data_list():
    # Read the list of initData strings from query.txt
    try:
        with open('query.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("query.txt not found.")
        return []

def authenticate(init_data):
    url = "https://app.ton.tsubasa-rivals.com/api/start"
    headers = {"accept": "application/json", "content-type": "application/json", "user-agent": "Mozilla/5.0"}
    payload = {"lang_code": "en", "initData": init_data}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        master_hash = data.get("master_hash")
        player_id = data.get("game_data", {}).get("user", {}).get("id")
        task_info_list = data.get("task_info", [])
        card_info = data.get("card_info", [])

        if player_id:
            print(f"Authenticated with Player ID: {player_id}")
            print("=========================================")
            print("Join Telegram Channel")
            print("https://t.me/dasarpemulung")
            print("=========================================")
        else:
            print("User information not found in the response.")
        return master_hash, player_id, task_info_list, card_info
    else:
        print("Failed to authenticate.")
        return None, None, None, None

def perform_action(url, master_hash, player_id, payload):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0",
        "x-masterhash": master_hash,
        "x-player-id": str(player_id)
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json() if response.status_code == 200 else None

def daily_checkin(master_hash, player_id, init_data):
    url = "https://app.ton.tsubasa-rivals.com/api/daily_reward/claim"
    payload = {"initData": init_data}
    result = perform_action(url, master_hash, player_id, payload)
    if result:
        for reward_info in result.get("daily_reward", []):
            if reward_info.get("gained"):
                print(f"Daily Reward Claimed: {reward_info.get('gained')}, Login Days: {reward_info.get('login_days')}, Reward Amount: {reward_info.get('reward')}")
                print("=========================================")
                print("Lagi Checkin, Otw ke proses selanjutnya")
                print("Join Telegram Channel : @dasarpemulung")
                print("YouTube : Dasar Pemulung")
                print("=========================================")

def execute_task(task_id, master_hash, player_id, init_data):
    url = "https://app.ton.tsubasa-rivals.com/api/task/execute"
    payload = {"task_id": task_id, "initData": init_data}
    return perform_action(url, master_hash, player_id, payload) is not None

def claim_task(task_id, master_hash, player_id, init_data):
    url = "https://app.ton.tsubasa-rivals.com/api/task/achievement"
    payload = {"task_id": task_id, "initData": init_data}
    result = perform_action(url, master_hash, player_id, payload)
    if result and "game_data" in result:
        print(f"Total Coin: {result.get('game_data', {}).get('user', {}).get('total_coins')}")
        print("=========================================")
        print("Lagi Claim Task Sabar Ya !!!")
        print("Join Telegram Channel : @dasarpemulung")
        print("YouTube : Dasar Pemulung")
        print("=========================================")
        return True
    return False

def upgrade_card(card_id, category_name, master_hash, player_id, init_data):
    url = "https://app.ton.tsubasa-rivals.com/api/card/levelup"
    payload = {"card_id": card_id, "category_id": category_name, "initData": init_data}
    result = perform_action(url, master_hash, player_id, payload)
    return result and "update" in result and "card" in result["update"]

def auto_upgrade_cards(card_info, master_hash, player_id, init_data, level_map):
    for category in card_info:
        category_name = category.get("category_name")
        target_level = level_map.get(category_name, 0)
        if not target_level:
            continue
        for card in category.get("card_list", []):
            card_id, current_level, unlocked = card.get("id"), card.get("level", 0), card.get("unlocked", False)
            if unlocked and current_level < target_level:
                while current_level < target_level:
                    if upgrade_card(card_id, category_name, master_hash, player_id, init_data):
                        current_level += 1
                        print(f"{category_name} Card {card_id} upgraded to level {current_level}.")
                        print("=========================================")
                        print("Lagi Proses Upgrade Card. Sabar ya !!!")
                        print("Join Telegram Channel : @dasarpemulung")
                        print("YouTube : Dasar Pemulung")
                        print("=========================================")
                    else:
                        break

def taptap(master_hash, player_id, init_data):
    url = "https://app.ton.tsubasa-rivals.com/api/tap"
    payload = {"initData": init_data, "tapCount": 100}
    result = perform_action(url, master_hash, player_id, payload)
    if result:
        print(f"Total Coin: {result.get('game_data', {}).get('user', {}).get('total_coins')}")
        print("=========================================")
        print("Lagi Proses Tap Tap. Sabar ya !!!")
        print("Join Telegram Channel : @dasarpemulung")
        print("YouTube : Dasar Pemulung")
        print("=========================================")

def main():
    enable_daily_checkin = input("Enable Daily Checkin? (y/n) [y]: ").strip().lower() or "y"
    enable_auto_clear_task = input("Enable Auto Clear Task? (y/n) [y]: ").strip().lower() or "y"
    enable_auto_taptap = input("Enable Auto Taptap? (y/n) [y]: ").strip().lower() or "y"
    level_map = {
        "Players": int(input("Auto Upgrade Card Player? Level (e.g., 10) [0]: ").strip() or 0),
        "Specials": int(input("Special Auto Upgrade Card Player? Level (e.g., 10) [0]: ").strip() or 0),
        "Coach": int(input("Coach Auto Upgrade Card? Level (e.g., 10) [0]: ").strip() or 0),
        "Manager": int(input("Auto Upgrade Card Manager? Level (e.g., 10) [0]: ").strip() or 0),
        "Stadium": int(input("Auto Upgrade Card Stadium? Level (e.g., 10) [0]: ").strip() or 0)
    }

    init_data_list = get_init_data_list()
    if not init_data_list:
        print("No initData entries found in query.txt. Exiting.")
        return

    for init_data in init_data_list:
        print("Processing account...")
        master_hash, player_id, task_info_list, card_info = authenticate(init_data)
        if master_hash and player_id:
            if enable_daily_checkin == "y":
                daily_checkin(master_hash, player_id, init_data)
            if enable_auto_clear_task == "y" and task_info_list:
                for task in task_info_list:
                    task_id = task.get("id")
                    if task_id and execute_task(task_id, master_hash, player_id, init_data):
                        claim_task(task_id, master_hash, player_id, init_data)
            if enable_auto_taptap == "y":
                taptap(master_hash, player_id, init_data)
            if card_info:
                auto_upgrade_cards(card_info, master_hash, player_id, init_data, level_map)

    print("All accounts have been processed.")
    print("=========================================")
    print("Proses telah di jalankan semua. Cooldown 30 Menit")
    print("Join Telegram Channel : @dasarpemulung")
    print("YouTube : Dasar Pemulung")
    print("=========================================")

    # Cooldown for 30 minutes before ending the script
    print("Cooldown for 30 minutes...")
    time.sleep(1800)  # Sleep for 30 minutes

if __name__ == "__main__":
    main()
