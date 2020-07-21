import logging
import threading
from dotenv import find_dotenv

from notifier import run_notifier
from sync_bot import run_bot

from settings import check_settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s (%(levelname)s) %(threadName)s - %(message)s')


def main():
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.name = 'TelegramBot'
    notifer_thread = threading.Thread(target=run_notifier)
    notifer_thread.name = 'Notifier'

    bot_thread.start()
    notifer_thread.start()

    logging.info('Threads started')


if __name__ == '__main__':
    if find_dotenv() is not '':
        main()
    else:
        logging.error('Cannot find .env with settings, terminate.')
