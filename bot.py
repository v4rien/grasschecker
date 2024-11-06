import requests
import json
from colorama import Fore, Style, init
import random
from fake_useragent import UserAgent

# Inisialisasi colorama
init(autoreset=True)

# Header untuk request HTTP
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,id;q=0.8",
    "origin": "https://app.getgrass.io",
    "priority": "u=1, i",
    "referer": "https://app.getgrass.io/",
    "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": UserAgent().random  # Menggunakan fake_useragent untuk menghasilkan user-agent acak
}

# Fungsi untuk menampilkan logo dan pesan
def print_logo():
    print(Fore.CYAN + r"""
    _____                      _____ _               _               
   / ____|                    / ____| |             | |            
  | |  __ _ __ __ _ ___ ___  | |    | |__   ___  ___| | _____ _ __ 
  | | |_ | '__/ _` / __/ __| | |    | '_ \ / _ \/ __| |/ / _ \ '__|
  | |__| | | | (_| \__ \__ \ | |____| | | |  __/ (__|   <  __/ |   
   \_____|_|  \__,_|___/___/  \_____|_| |_|\___|\___|_|\_\___|_|   
                                                                  
    """)

# Fungsi untuk membaca username dan password dari file
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

# Fungsi untuk membaca proxy dari file
def read_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = file.read().splitlines()
    return proxies

# Fungsi untuk login dan mendapatkan token, bisa menggunakan proxy jika diperlukan
def login_and_get_token(username, password, proxy=None):
    url = "https://api.getgrass.io/login"
    payload = {"username": username, "password": password}

    # Tentukan proxies jika ada
    proxies = None
    if proxy:
        proxies = {
            "http": proxy,
            "https": proxy
        }

    # Kirim request login dengan atau tanpa proxy
    response = requests.post(url, json=payload, headers=HEADERS, proxies=proxies)

    if response.status_code == 200:
        try:
            access_token = response.json()["result"]["data"]["accessToken"]
            return access_token
        except KeyError:
            print("Error: Tidak dapat menemukan accessToken dalam respons.")
            
    return None

# Inisialisasi UserAgent dari fake_useragent
ua = UserAgent()

# Fungsi untuk mendapatkan data pengguna
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

# Fungsi untuk menghitung jumlah perangkat aktif
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

# Fungsi utama untuk memproses semua akun
def process_accounts(auth_file_path, proxy_file_path, use_proxy=False):
    credentials = read_credentials(auth_file_path)
    proxies = read_proxies(proxy_file_path) if use_proxy else None

    if use_proxy and len(proxies) < 1:
        print(Fore.RED + "Error: Tidak ada proxy yang tersedia.")
        return

    print_logo()
    
    for idx, (username, password) in enumerate(credentials):
        selected_proxy = random.choice(proxies) if use_proxy else None
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

# Menyediakan path ke file token dan file proxy
auth_file_path = 'user.txt'
proxy_file_path = 'proxy.txt'

# Tanyakan apakah ingin menggunakan proxy atau tidak
use_proxy = input("Do you want to use proxy? (y/n): ").strip().lower() == 'y'

# Memproses akun dengan file teks yang berisi token dan proxy
process_accounts(auth_file_path, proxy_file_path, use_proxy)
