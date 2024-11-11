import requests
import json
from colorama import Fore, Style, init
from fake_useragent import UserAgent

init(autoreset=True)

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,id;q=0.8",
    "origin": "https://app.getgrass.io",
    "priority": "u=1, i",
    "referer": "https://app.getgrass.io/",
    "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": UserAgent().random
}

def print_logo():
    print(Fore.CYAN + r"""
    _____                      _____ _               _               
   / ____|                    / ____| |             | |            
  | |  __ _ __ __ _ ___ ___  | |    | |__   ___  ___| | _____ _ __ 
  | | |_ | '__/ _` / __/ __| | |    | '_ \ / _ \/ __| |/ / _ \ '__|
  | |__| | | | (_| \__ \__ \ | |____| | | |  __/ (__|   <  __/ |   
   \_____|_|  \__,_|___/___/  \_____|_| |_|\___|\___|_|\_\___|_|   
                                                                  
    """)

def read_credentials(file_path="user.txt"):
    credentials = []
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line:
                username, password = line.split(":")
                credentials.append((username, password))
    return credentials

def login_and_get_token(username, password):
    url = "https://api.getgrass.io/login"
    payload = {"username": username, "password": password}

    response = requests.post(url, json=payload, headers=HEADERS)
    
    if response.status_code == 200:
        try:
            access_token = response.json()["result"]["data"]["accessToken"]
            return access_token
        except KeyError:
            print("Error: Tidak dapat menemukan accessToken dalam respons.")
    return None

ua = UserAgent()

def get_user_data(authorization_token, user_agent):
    url = "https://api.getgrass.io/retrieveUser"
    
    headers = HEADERS.copy()
    headers["authorization"] = authorization_token
    headers["user-agent"] = user_agent

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        if response.status_code == 401:
            print(f"Unauthorized: Token {authorization_token} tidak valid!")
            return None

        data = response.json()
        if "result" in data and "data" in data["result"]:
            user_data = data["result"]["data"]
            email = user_data["email"]
            user_id = user_data["userId"]
            total_points = user_data["totalPoints"]

            formatted_points = "{:,}".format(total_points)
            return email, user_id, formatted_points
        else:
            print("Data tidak ditemukan dalam response.")
            return None
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP error occurred: {errh}")
    except requests.exceptions.RequestException as err:
        print(f"Other error occurred: {err}")
    
    return None

def get_active_devices(authorization_token, user_agent):
    url = "https://api.getgrass.io/activeDevices"
    
    headers = HEADERS.copy()
    headers["authorization"] = authorization_token
    headers["user-agent"] = user_agent

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        if response.status_code == 401:
            print(f"Unauthorized: Token {authorization_token} tidak valid!")
            return 0

        data = response.json()
        if "result" in data and "data" in data["result"]:
            active_devices = data["result"]["data"]
            return len(active_devices)
        else:
            print("Data perangkat aktif tidak ditemukan dalam response.")
            return 0
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP error occurred: {errh}")
    except requests.exceptions.RequestException as err:
        print(f"Other error occurred: {err}")
    
    return 0

def process_accounts(auth_file_path):
    credentials = read_credentials(auth_file_path)

    print_logo()
    print(Fore.YELLOW + "Running bot without proxy...")

    for idx, (username, password) in enumerate(credentials):
        access_token = login_and_get_token(username, password)
        
        if access_token is None:
            print(Fore.RED + f"Login gagal untuk akun {username}.")
            continue

        user_agent = ua.random
        
        print(Fore.CYAN + f"--------------------Account {idx + 1}--------------------")
        
        user_data = get_user_data(access_token, user_agent)

        if user_data:
            email, user_id, total_points = user_data
            print(f"Email: {email}")
            print(f"User ID: {user_id}")
            print(Fore.GREEN + f"Total Points: {total_points}")
            
            active_devices_count = get_active_devices(access_token, user_agent)
            print(Fore.YELLOW + f"Connected Device: {active_devices_count}")
        else:
            print(Fore.RED + f"Error occurred while processing Account {username}.")
        
        print(Fore.CYAN + "-------------------------------------------------")

auth_file_path = 'user.txt'

process_accounts(auth_file_path)
