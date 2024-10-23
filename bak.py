import time
import requests

def read_init_data(file_path):
    # Read initData from the specified file
    with open(file_path, 'r') as file:
        return file.read().strip()

def get_file_list():
    # Read the list of files from query.txt
    try:
        with open('query.txt', 'r') as file:
            file_list = [line.strip() for line in file if line.strip()]
        return file_list
    except FileNotFoundError:
        print("query.txt not found.")
        return []

def authenticate(init_data):
    # URL for authentication
    url = "https://app.ton.tsubasa-rivals.com/api/start"
    
    # Simplified headers
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0"
    }
    
    # Payload for authentication
    payload = {
        "lang_code": "en",
        "initData": init_data
    }
    
    # Send the POST request for authentication
    response = requests.post(url, headers=headers, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract user information and relevant data
        master_hash = data.get("master_hash")
        player_id = data.get("game_data", {}).get("user", {}).get("id")
        task_info_list = data.get("task_info", [])
        card_info = data.get("card_info", [])
        
        if player_id:
            print(f"Authenticated with Player ID: {player_id}")
        else:
            print("User information not found in the response.")
        
        # Return the master_hash, player_id, task_info, and card_info
        return master_hash, player_id, task_info_list, card_info
    else:
        print("Failed to authenticate.")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return None, None, None, None

def daily_checkin(master_hash, player_id):
    # URL for the daily check-in
    url = "https://app.ton.tsubasa-rivals.com/api/daily_reward/claim"
    
    # Headers with x-masterhash and x-player-id
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0",
        "x-masterhash": master_hash,
        "x-player-id": str(player_id)
    }
    
    # Read initData for the request payload
    init_data = read_init_data()
    payload = {
        "initData": init_data
    }
    
    # Send the POST request
    response = requests.post(url, headers=headers, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Print only the daily reward information where "gained" is True
        daily_reward = data.get("daily_reward", [])
        for reward_info in daily_reward:
            if reward_info.get('gained'):
                # Display the required information
                print(f"Daily Reward Claimed: {reward_info.get('gained')}")
                print(f"Login Days: {reward_info.get('login_days')}")
                print(f"Reward Amount: {reward_info.get('reward')}")
    else:
        print("Failed to claim daily reward.")

def execute_task(task_id, master_hash, player_id):
    # URL for executing the task
    url = "https://app.ton.tsubasa-rivals.com/api/task/execute"
    
    # Headers with x-masterhash and x-player-id
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0",
        "x-masterhash": master_hash,
        "x-player-id": str(player_id)
    }
    
    # Read initData for the request payload
    init_data = read_init_data()
    payload = {
        "task_id": task_id,
        "initData": init_data
    }
    
    # Send the POST request to execute the task
    response = requests.post(url, headers=headers, json=payload)
    
    # Check if the request was successful
    return response.status_code == 200

def claim_task(task_id, master_hash, player_id):
    # URL for claiming the task reward
    url = "https://app.ton.tsubasa-rivals.com/api/task/achievement"
    
    # Headers with x-masterhash and x-player-id
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0",
        "x-masterhash": master_hash,
        "x-player-id": str(player_id)
    }
    
    # Read initData for the request payload
    init_data = read_init_data()
    payload = {
        "task_id": task_id,
        "initData": init_data
    }
    
    # Send the POST request to claim the reward
    response = requests.post(url, headers=headers, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Ensure that data is not None and contains the "update" field
        if data and "update" in data:
            # Extract and print the task title from the response
            task_info = data.get("game_data", {}).get("user", {})
            if task_info:
                print(f"Total Coin: {task_info.get('total_coins')}")
                return True
            else:
                print("No task information found in the response.")
        else:
            print("The response does not contain the expected 'update' field.")
    else:
        print("Failed to claim the task.")
    return False

def upgrade_card(card_id, category_name, master_hash, player_id):
    # URL for upgrading the card
    url = "https://app.ton.tsubasa-rivals.com/api/card/levelup"
    
    # Headers with x-masterhash and x-player-id
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0",
        "x-masterhash": master_hash,
        "x-player-id": str(player_id)
    }
    
    # Read initData for the request payload
    init_data = read_init_data()
    payload = {
        "card_id": card_id,
        "category_id": category_name,
        "initData": init_data
    }
    
    # Send the POST request to upgrade the card
    response = requests.post(url, headers=headers, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Check if the card was upgraded successfully
        card_data = data.get("update", {}).get("card", {})
        if card_data and card_data.get("level") is not None:
            return True
        else:
            print(f"Failed to upgrade card {card_id}. Response: {data}")
            return False
    else:
        print(f"Failed to upgrade card {card_id}. HTTP Status: {response.status_code}")
        return False


def auto_upgrade_cards(card_info, master_hash, player_id, player_level, special_level, coach_level, manager_level, stadium_level):
    # Mapping category names to their respective level limits
    category_levels = {
        "Players": player_level,
        "Specials": special_level,
        "Coach": coach_level,
        "Manager": manager_level,
        "Stadium": stadium_level
    }

    # Iterate over the card_info list to process each category
    for category in card_info:
        category_name = category.get("category_name")
        card_list = category.get("card_list", [])

        # Process each card in the card_list
        for card in card_list:
            card_id = card.get("id")
            current_level = card.get("level", 0)
            unlocked = card.get("unlocked", False)

            # Check if the necessary fields are present
            if not card_id or not category_name:
                print(f"Skipping card with missing information. Card ID: {card_id}, Category: {category_name}")
                continue

            # Check if the card is unlocked and the category is in the specified levels
            if unlocked and category_name in category_levels:
                target_level = category_levels[category_name]
                # Upgrade the card up to the target level if current level is lower
                while current_level < target_level:
                    print(f"Upgrading {category_name} Card {card_id} from level {current_level} to {current_level + 1}...")
                    success = upgrade_card(card_id, category_name, master_hash, player_id)
                    if success:
                        current_level += 1
                        print(f"{category_name} Card {card_id} upgraded to level {current_level}.")
                    else:
                        print(f"Failed to upgrade {category_name} Card {card_id}. Skipping to the next card.")
                        break
            else:
                print(f"Skipping {category_name} Card {card_id}. Either it's locked or not in the specified categories.")



def taptap(master_hash, player_id):
    # URL for claiming the task reward
    url = "https://app.ton.tsubasa-rivals.com/api/tap"
    
    # Headers with x-masterhash and x-player-id
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0",
        "x-masterhash": master_hash,
        "x-player-id": str(player_id)
    }
    
    # Read initData for the request payload
    init_data = read_init_data()
    payload = {
        "initData": init_data,
        "tapCount": 100
    }
    
    # Send the POST request to claim the reward
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        # Ensure that data is not None and contains the "update" field
        if data :
            # Extract and print the task title from the response
            taptap = data.get("game_data", {}).get("user", {})
            if taptap:
                print(f"Total Coin: {taptap.get('total_coins')}")
                return True
            else:
                print("Erro Getting Total Coin response.")
        else:
            print("Error Pasing gamedata")
    else:
        print("Failed to taptap.")
    return False

def main():
    # Ask the user for input on each feature
    enable_daily_checkin = input("Enable Daily Checkin? (y/n) [y]: ").strip().lower() or "y"
    enable_auto_clear_task = input("Enable Auto Clear Task? (y/n) [y]: ").strip().lower() or "y"
    enable_auto_taptap = input("Enable Auto Taptap? (y/n) [y]: ").strip().lower() or "y"

    # Ask for upgrade levels for different card categories
    player_upgrade_level = int(input("Auto Upgrade Card Player? Fill in the level (e.g., 10) [0]: ").strip() or 0)
    special_upgrade_level = int(input("Special Auto Upgrade Card Player? Fill in the level (e.g., 10) [0]: ").strip() or 0)
    coach_upgrade_level = int(input("Coach Auto Upgrade Card? Fill in the level (e.g., 10) [0]: ").strip() or 0)
    manager_upgrade_level = int(input("Auto Upgrade Card Manager? Fill in the level (e.g., 10) [0]: ").strip() or 0)
    stadium_upgrade_level = int(input("Auto Upgrade Card Stadium? Fill in the level (e.g., 10) [0]: ").strip() or 0)

    # Authenticate and get the necessary details
    master_hash, player_id, task_info_list, card_info = authenticate()
    if master_hash and player_id:
        # Perform daily check-in if enabled
        if enable_daily_checkin == "y":
            print("Performing Daily Checkin...")
            daily_checkin(master_hash, player_id)
        else:
            print("Daily Checkin is skipped.")

        # Proceed to task execution if enabled and tasks are available
        if enable_auto_clear_task == "y":
            if task_info_list:
                for task_info in task_info_list:
                    task_id = task_info.get("id")
                    if task_id:
                        print(f"Executing Task ID: {task_id}")
                        if execute_task(task_id, master_hash, player_id):
                            print("Task executed successfully.")
                            # Try to claim the task reward
                            if claim_task(task_id, master_hash, player_id):
                                print("Task reward claimed successfully.")
                            else:
                                print("Failed to claim task reward.")
                        else:
                            print("Task execution failed.")
                    else:
                        print("No valid task ID found for the current task.")
            else:
                print("No task information available.")
        else:
            print("Auto Clear Task is skipped.")

        # Perform TapTap action if enabled
        if enable_auto_taptap == "y":
            print("Performing TapTap action...")
            if taptap(master_hash, player_id):
                print("TapTap action completed successfully.")
            else:
                print("Failed to perform TapTap action.")
        else:
            print("TapTap action is skipped.")

        # Perform card upgrades based on user input
        if card_info:
            auto_upgrade_cards(card_info, master_hash, player_id, player_upgrade_level, special_upgrade_level,
                               coach_upgrade_level, manager_upgrade_level, stadium_upgrade_level)
        else:
            print("No card information available.")
    else:
        print("Failed to authenticate.")


# Entry point for the script
if __name__ == "__main__":
    main()
