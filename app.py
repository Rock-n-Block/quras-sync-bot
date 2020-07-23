import logging
import threading
from dotenv import find_dotenv

from notifier import run_notifier
from sync_bot import run_bot

logging.basicConfig(level=logging.INFO, format='%(asctime)s (%(levelname)s) %(threadName)s - %(message)s')


def continuous_thread(thread_process):
    def wrapper():
        while True:
            try:
                thread_process()
            except BaseException as e:
                logging.error('Error in thread execution')
                logging.error(e)
                logging.info('Restarting thread')
            else:
                logging.info('Thread exited, restarting')
    return wrapper


@continuous_thread
def notifier_process():
    run_notifier()


@continuous_thread
def bot_process():
    run_bot()


def main():
    bot_thread = threading.Thread(target=continuous_thread(bot_process), name='TelegramBot')
    bot_thread.start()

    notifer_thread = threading.Thread(target=continuous_thread(notifier_process), name='Notifier')
    notifer_thread.start()

    logging.info('Threads started')


if __name__ == '__main__':
    if find_dotenv() is not '':
        main()
    else:
        logging.error('Cannot find .env with settings, terminate.')
