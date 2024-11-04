import requests
import json
import random
import time
from datetime import datetime, timedelta, timezone
import pytz
from colorama import Fore, Style

def load_tokens(filename="akun.txt"):
    with open(filename, "r") as file:
        return ["Bearer " + line.strip() for line in file]

tokens = load_tokens()

def load_user_agents(filename="useragents.json"):
    with open(filename, "r") as file:
        return json.load(file)

user_agents = load_user_agents()

def get_random_user_agent():
    return random.choice(user_agents)

def get_headers(token):
    return {
        "accept": "/",
        "accept-language": "en-GB,en;q=0.8",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://tg-tap-miniapp.laborx.io",
        "priority": "u=1, i",
        "referer": "https://tg-tap-miniapp.laborx.io/",
        "sec-ch-ua": '"Brave";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": get_random_user_agent(),
    }

def get_farming_info(token):
    try:
        response = requests.get(
            "https://tg-bot-tap.laborx.io/api/v1/farming/info",
            headers=get_headers(token)
        )
        if response.status_code == 200:
            data = response.json()
            balance = data.get("balance")
            active_farming_started_at = data.get("activeFarmingStartedAt")
            farming_duration_in_sec = data.get("farmingDurationInSec")
            
            if active_farming_started_at:
                
                try:
                    utc_time = datetime.strptime(active_farming_started_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                    active_farming_started_wib = utc_time.replace(tzinfo=timezone.utc).astimezone(pytz.timezone("Asia/Jakarta")).strftime('%Y-%m-%d %H:%M:%S')
                    next_claim_time = (utc_time + timedelta(seconds=farming_duration_in_sec + 10)).astimezone(pytz.timezone("Asia/Jakarta")).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"{Fore.GREEN}Balance: {balance}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}Active Farming Started At (WIB): {active_farming_started_wib}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}Next Claim Time (WIB): {next_claim_time}{Style.RESET_ALL}")
                except ValueError as e:
                    print(f"{Fore.RED}Error parsing date: {e}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}Farming has not started yet{Style.RESET_ALL}")

            return {"activeFarmingStartedAt": active_farming_started_at, "farmingDurationInSec": farming_duration_in_sec}
        else:
            print(f"{Fore.RED}Gagal mendapatkan info farming: {response.status_code}{Style.RESET_ALL}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Terjadi error: {e}{Style.RESET_ALL}")
    return None

def start_farming(token, index):
    try:
        response = requests.post(
            "https://tg-bot-tap.laborx.io/api/v1/farming/start",
            headers=get_headers(token),
            data={}
        )
        if response.status_code == 200:
            print(f"{Fore.GREEN}Account {index + 1} successfully started farming{Style.RESET_ALL}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Account {index + 1} Error starting farming: {e}{Style.RESET_ALL}")

def finish_farming(token, index):
    try:
        response = requests.post(
            "https://tg-bot-tap.laborx.io/api/v1/farming/finish",
            headers=get_headers(token),
            data={}
        )
        if response.status_code == 200:
            print(f"{Fore.GREEN}Account {index + 1} successfully finished farming{Style.RESET_ALL}")
            time.sleep(3)
            start_farming(token, index)
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Account {index + 1} Error finishing farming: {e}{Style.RESET_ALL}")

def run_account(token, index):
    print(f"{Fore.BLUE}★*****************★{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Processing account {index + 1}...{Style.RESET_ALL}")
    farming_info = get_farming_info(token)

    if farming_info:
        if farming_info["activeFarmingStartedAt"]:
            next_claim_time = (datetime.strptime(farming_info["activeFarmingStartedAt"], '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(seconds=farming_info["farmingDurationInSec"] + 10)).replace(tzinfo=timezone.utc).astimezone(pytz.timezone("Asia/Jakarta"))
            wait_time = (next_claim_time - datetime.now(pytz.timezone("Asia/Jakarta"))).total_seconds()
            hours, minutes = divmod(wait_time / 60, 60)
            print(f"{Fore.BLACK}Waiting {int(hours)} hours and {int(minutes)} minutes before claiming...{Style.RESET_ALL}")
            time.sleep(max(0, wait_time))
            finish_farming(token, index)
        else:
            print(f"{Fore.BLUE}Starting farming for account {index + 1}...{Style.RESET_ALL}")
            start_farming(token, index)

def start_claiming():
    while True:
        for index, token in enumerate(tokens):
            run_account(token, index)
            time.sleep(5)
        print(f"{Fore.BLUE}Waiting 1 hour before starting again...{Style.RESET_ALL}")
        time.sleep(3600)

start_claiming()
