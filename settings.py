import os

from dotenv import load_dotenv, find_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ETHERSCAN_TOKEN = os.getenv('ETHERSCAN_TOKEN')

PARITY_IP = os.getenv('PARITY_IP')
PARITY_PORT = os.getenv('PARITY_PORT')

POSTGRES_AUTH = {
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASS'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT'),
    'database': os.getenv('POSTGRES_DB')
}


ALERT_BLOCK_DIFFERENCE = int(os.getenv('ALERT_BLOCK_DIFFERENCE'))
