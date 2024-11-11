import requests
import json
import os
from colorama import Fore, Style, init
import random
from fake_useragent import UserAgent

os.system('cls' if os.name == 'nt' else 'clear')
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

def read_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = file.read().splitlines()
    return proxies

def login_and_get_token(username, password, proxy=None):
    url = "https://api.getgrass.io/login"
    payload = {"username": username, "password": password}
    proxies = {"http": proxy, "https": proxy} if proxy else None

    try:
        response = requests.post(url, json=payload, headers=HEADERS, proxies=proxies, timeout=10)
        if response.status_code == 200:
            try:
                access_token = response.json()["result"]["data"]["accessToken"]
                return access_token
            except KeyError:
                pass
    except requests.exceptions.RequestException:
        pass

    return None

ua = UserAgent()

def get_user_data(authorization_token, user_agent, proxy=None):
    url = "https://api.getgrass.io/retrieveUser"
    headers = HEADERS.copy()
    headers["authorization"] = authorization_token
    headers["user-agent"] = user_agent
    proxies = {"http": proxy, "https": proxy} if proxy else None

    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()

        if response.status_code == 401:
            return None
        
        data = response.json()
        if "result" in data and "data" in data["result"]:
            user_data = data["result"]["data"]
            email = user_data["email"]
            user_id = user_data["userId"]
            total_points = user_data["totalPoints"]
            formatted_points = "{:,}".format(total_points)
            return email, user_id, formatted_points
    except requests.exceptions.RequestException:
        pass
    
    return None

def get_active_devices(authorization_token, user_agent, proxy=None):
    url = "https://api.getgrass.io/activeDevices"
    headers = HEADERS.copy()
    headers["authorization"] = authorization_token
    headers["user-agent"] = user_agent
    proxies = {"http": proxy, "https": proxy} if proxy else None

    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()

        if response.status_code == 401:
            return 0

        data = response.json()
        if "result" in data and "data" in data["result"]:
            active_devices = data["result"]["data"]
            return len(active_devices)
    except requests.exceptions.RequestException:
        pass
    
    return 0

def process_accounts(auth_file_path, proxy_file_path):
    credentials = read_credentials(auth_file_path)
    proxies = read_proxies(proxy_file_path)
    print_logo()

    if len(proxies) < 1:
        print(Fore.RED + "Error: Tidak ada proxy yang tersedia.")
        return

    print(Fore.YELLOW + "Running bot with proxy...")
    used_proxies = []

    for idx, (username, password) in enumerate(credentials):
        selected_proxy = None
        available_proxies = [proxy for proxy in proxies if proxy not in used_proxies]
        if available_proxies:
            selected_proxy = random.choice(available_proxies)
            used_proxies.append(selected_proxy)
        else:
            print(Fore.RED + f"Tidak ada proxy yang tersisa untuk akun {username}.")
            break

        access_token = None
        while not access_token:
            access_token = login_and_get_token(username, password, proxy=selected_proxy)
            if not access_token:
                used_proxies.remove(selected_proxy)
                proxies.remove(selected_proxy)
                if proxies:
                    available_proxies = [proxy for proxy in proxies if proxy not in used_proxies]
                    if available_proxies:
                        selected_proxy = random.choice(available_proxies)
                        used_proxies.append(selected_proxy)
                    else:
                        print(Fore.RED + "Tidak ada proxy yang tersisa, proses login gagal.")
                        break

        if access_token:
            user_agent = ua.random
            print(Fore.CYAN + f"--------------------Account {idx + 1}--------------------")
            print(f"Proxy: {selected_proxy}")
            
            user_data = get_user_data(access_token, user_agent, proxy=selected_proxy)
            if user_data:
                email, user_id, total_points = user_data
                print(f"Email: {email}")
                print(f"User ID: {user_id}")
                print(Fore.GREEN + f"Total Points: {total_points}")
                
                active_devices_count = get_active_devices(access_token, user_agent, proxy=selected_proxy)
                print(Fore.YELLOW + f"Connected Device: {active_devices_count}")
            else:
                print(Fore.RED + f"Error occurred while processing Account {username}.")
            
            print(Fore.CYAN + "-------------------------------------------------")
        else:
            print(Fore.RED + f"Login gagal untuk akun {username}.")

auth_file_path = 'user.txt'
proxy_file_path = 'proxy.txt'

process_accounts(auth_file_path, proxy_file_path)
