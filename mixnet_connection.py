from mixnet_client import MixnetClient
from os import getenv
from dotenv import load_dotenv
import requests
import time

requests.packages.urllib3.disable_warnings()

load_dotenv()

mixnet_entry = getenv('MIXNET_ENTRY')
port = int(getenv('PORT'))

def start_test():
    while True:
        response = requests.get('https://pets.kmoragas.com/log/3-wa92tywpZb17N86jdOctpTWw6XwHGkyaVwPjWDGI3tA=/exit.txt',verify=False)
        q = response.content.decode().count('encrypted')
        print(q)
        # time.sleep(5)


start_test()