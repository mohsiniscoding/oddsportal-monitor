## create a telegram bot that has a helper function to send message on a specific chat_id

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

def send_message(message):
    ## send message to a specific chat_id
    url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
    requests.get(url)

def get_updates():
    ## get all new messages
    url = f'https://api.telegram.org/bot{token}/getUpdates'
    response = requests.get(url)
    return response.json()

if __name__ == '__main__':
    print(get_updates())
    input("Press ENTER to continue:")
    send_message('Hello World!')
    input("Press ENTER to continue:")
    print(get_updates())

