import requests
import json
from colorama import Fore, Style, init
import random
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

def read_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = file.read().splitlines()
    return proxies

def test_proxy(proxy):
    test_url = "https://httpbin.org/ip"
    try:
        response = requests.get(test_url, proxies={"http": proxy, "https": proxy}, timeout=5)
        if response.status_code == 200:
            return True
    except requests.RequestException:
        return False

def login_and_get_token(username, password, proxy=None):
    url = "https://api.getgrass.io/login"
    payload = {"username": username, "password": password}
    proxies = None
    if proxy:
        proxies = {
            "http": proxy,
            "https": proxy
        }
    response = requests.post(url, json=payload, headers=HEADERS, proxies=proxies)
    if response.status_code == 200:
        try:
            access_token = response.json()["result"]["data"]["accessToken"]
            return access_token
        except KeyError:
            print("Error: Tidak dapat menemukan accessToken dalam respons.")
    return None

ua = UserAgent()

def get_user_data(authorization_token, user_agent, proxy=None):
    url = "https://api.getgrass.io/retrieveUser"
    headers = HEADERS.copy()
    headers["authorization"] = authorization_token
    headers["user-agent"] = user_agent
    proxies = None
    if proxy:
        proxies = {
            "http": proxy,
            "https": proxy
        }
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
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

def get_active_devices(authorization_token, user_agent, proxy=None):
    url = "https://api.getgrass.io/activeDevices"
    headers = HEADERS.copy()
    headers["authorization"] = authorization_token
    headers["user-agent"] = user_agent
    proxies = None
    if proxy:
        proxies = {
            "http": proxy,
            "https": proxy
        }
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
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

def process_accounts(auth_file_path, proxy_file_path, use_proxy=False):
    credentials = read_credentials(auth_file_path)
    print_logo()
    if not use_proxy:
        print(Fore.YELLOW + "Running bot without proxy...")
    if use_proxy:
        proxies = read_proxies(proxy_file_path)
        if len(proxies) < 1:
            print(Fore.RED + "Error: Tidak ada proxy yang tersedia.")
            return
        print(Fore.YELLOW + "Running bot with proxy...")
        active_proxies = [proxy for proxy in proxies if test_proxy(proxy)]
        if not active_proxies:
            print(Fore.RED + "Error: Tidak ada proxy yang aktif.")
            return
        used_proxies = []
    else:
        active_proxies = []
        used_proxies = []

    for idx, (username, password) in enumerate(credentials):
        selected_proxy = None
        if use_proxy:
            available_proxies = [proxy for proxy in active_proxies if proxy not in used_proxies]
            if not available_proxies:
                print(Fore.RED + "Error: Tidak ada proxy yang tersedia untuk akun-akun yang tersisa.")
                break
            selected_proxy = random.choice(available_proxies)
            used_proxies.append(selected_proxy)
        access_token = login_and_get_token(username, password, proxy=selected_proxy)
        if access_token is None:
            print(Fore.RED + f"Login gagal untuk akun {username}.")
            continue
        user_agent = ua.random
        print(Fore.CYAN + f"--------------------Account {idx + 1}--------------------")
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

auth_file_path = 'user.txt'
proxy_file_path = 'proxy.txt'

use_proxy = input("Do you want to use proxy? (y/n): ").strip().lower() == 'y'

process_accounts(auth_file_path, proxy_file_path, use_proxy)
