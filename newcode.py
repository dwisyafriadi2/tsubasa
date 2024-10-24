import time
import requests

# Inisialisasi header umum yang akan digunakan
BASE_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    "origin": "https://app.ton.tsubasa-rivals.com",
    "referer": "https://app.ton.tsubasa-rivals.com/",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "priority": "u=1, i",
    "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129", "Microsoft Edge WebView2";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site"
}

def get_init_data_list():
    try:
        with open('query.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("query.txt tidak ditemukan.")
        return []

def authenticate(init_data):
    url = "https://api.app.ton.tsubasa-rivals.com/api/start"
    headers = BASE_HEADERS.copy()
    payload = {
        "initData": init_data,
        "lang_code": "en"
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)
    if response.status_code == 200:
        data = response.json()
        master_hash = data.get("master_hash")
        player_id = data.get("game_data", {}).get("user", {}).get("id")
        task_info_list = data.get("task_info", [])
        card_info = data.get("card_info", [])

        if player_id:
            print(f"Authenticated with Player ID: {player_id}")
            print("=========================================")
            print("Proses telah di jalankan semua. Cooldown 30 Menit")
            print("Join Telegram Channel : @dasarpemulung")
            print("YouTube : Dasar Pemulung")
            print("=========================================")
        else:
            print("User information not found in the response.")
        return master_hash, player_id, task_info_list, card_info
    else:
        print("Failed to authenticate.")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return None, None, None, None

def perform_action(url, master_hash, player_id, payload, max_retries=5):
    headers = BASE_HEADERS.copy()
    headers.update({
        "x-masterhash": master_hash,
        "x-player-id": str(player_id)
    })
    
    retry_count = 0
    while retry_count < max_retries:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            wait_time = 2 ** retry_count  # Exponential backoff
            print(f"Rate limit hit. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            retry_count += 1
        else:
            print(f"Request to {url} failed. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    print(f"Failed to perform action after {max_retries} retries.")
    return None

def daily_checkin(master_hash, player_id, init_data):
    url = "https://api.app.ton.tsubasa-rivals.com/api/daily_reward/claim"
    payload = {
        "initData": init_data
    }
    result = perform_action(url, master_hash, player_id, payload)
    if result:
        daily_reward = result.get("daily_reward", [])
        if daily_reward:
            for reward_info in daily_reward:
                if reward_info.get("gained"):
                    print(f"Daily Reward Claimed: {reward_info.get('gained')}, Login Days: {reward_info.get('login_days')}, Reward Amount: {reward_info.get('reward')}")
                    print("=========================================")
                    print("Join Telegram Channel : @dasarpemulung")
                    print("YouTube : Dasar Pemulung")
                    print("=========================================")
        else:
            print("No daily rewards found.")
    else:
        print("Failed to perform daily check-in.")

def execute_task(task_id, master_hash, player_id, init_data):
    url = "https://api.app.ton.tsubasa-rivals.com/api/task/execute"
    payload = {
        "task_id": task_id,
        "initData": init_data
    }
    result = perform_action(url, master_hash, player_id, payload)
    if result:
        print(f"Task {task_id} executed successfully.")
        return True
    else:
        print(f"Failed to execute task {task_id}.")
        return False

def claim_task(task_id, master_hash, player_id, init_data):
    url = "https://api.app.ton.tsubasa-rivals.com/api/task/achievement"
    payload = {
        "task_id": task_id,
        "initData": init_data
    }
    result = perform_action(url, master_hash, player_id, payload)
    if result:
        total_coins = result.get("game_data", {}).get("user", {}).get("total_coins", 0)
        print(f"Task {task_id} claimed successfully. Total Coins: {total_coins}")
        return True
    else:
        print(f"Failed to claim task {task_id}.")
        return False

def taptap(master_hash, player_id, init_data):
    url = "https://api.app.ton.tsubasa-rivals.com/api/tap"
    payload = {
        "initData": init_data,
        "tapCount": 100
    }

    # Mengirim permintaan TapTap sebanyak 10 kali dengan delay 30 detik
    for i in range(10):
        print(f"Performing TapTap action {i + 1}/10...")
        result = perform_action(url, master_hash, player_id, payload)
        if result:
            total_coins = result.get("game_data", {}).get("user", {}).get("total_coins", 0)
            print(f"TapTap action {i + 1} completed. Total Coins: {total_coins}")
        else:
            print(f"Failed to perform TapTap action {i + 1}.")

        # Delay 30 detik sebelum permintaan berikutnya
        if i < 9:  # Tidak menunggu setelah permintaan terakhir
            print("Waiting for 30 seconds before the next TapTap...")
            time.sleep(10)

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
                    else:
                        print(f"Failed to upgrade {category_name} Card {card_id}.")
                        break

def upgrade_card(card_id, category_name, master_hash, player_id, init_data):
    url = "https://api.app.ton.tsubasa-rivals.com/api/card/levelup"
    payload = {
        "card_id": card_id,
        "category_id": category_name,
        "initData": init_data
    }
    result = perform_action(url, master_hash, player_id, payload)
    if result:
        card_info = result.get("update", {}).get("card", {})
        if card_info:
            print(f"Card {card_id} upgraded successfully to level {card_info.get('level')}.")
            return True
    return False

def main():
    enable_daily_checkin = input("Enable Daily Checkin? (y/n) [y]: ").strip().lower() or "y"
    enable_auto_clear_task = input("Enable Auto Clear Task? (y/n) [y]: ").strip().lower() or "y"
    enable_auto_taptap = input("Enable Auto Taptap? (y/n) [y]: ").strip().lower() or "y"
    level_map = {
        "Players": int(input("Auto Upgrade Card Player? Level (e.g., 10) [0]: ").strip() or 0),
        "Specials": int(input("Auto Upgrade Card Specials? Level (e.g., 10) [0]: ").strip() or 0),
        "Coach": int(input("Auto Upgrade Card Coach? Level (e.g., 10) [0]: ").strip() or 0),
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
                print("Performing daily check-in...")
                daily_checkin(master_hash, player_id, init_data)
            
            if enable_auto_clear_task == "y" and task_info_list:
                print("Executing tasks...")
                for task in task_info_list:
                    task_id = task.get("id")
                    if task_id and execute_task(task_id, master_hash, player_id, init_data):
                        claim_task(task_id, master_hash, player_id, init_data)
            
            if enable_auto_taptap == "y":
                print("Performing TapTap...")
                taptap(master_hash, player_id, init_data)
            
            if card_info:
                print("Auto-upgrading cards...")
                auto_upgrade_cards(card_info, master_hash, player_id, init_data, level_map)
        
        print("Account processing completed.")
        print("=========================================")

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
