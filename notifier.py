from datetime import datetime
from time import sleep
import logging

from status_fetcher import get_sync_status, CommonFetchException, status_to_text
from database_api import save_update_status_core_common, get_from_status_core
from sync_bot import bot, send_to_all

from settings import ALERT_BLOCK_DIFFERENCE


def generate_alert_message(current_status):
    status_text = status_to_text(current_status)
    alert_text = 'ALERT! Difference is deterministic! \n \n' + status_text
    return alert_text


def is_current_status_alert(sync_status):
    etherscan_blocks = sync_status['etherscan']
    parity_blocks = sync_status['parity']
    bitcore_blocks = sync_status['bitcore']

    logging.info(sync_status)

    # etherscan_blocks += 55
    alert_etherscan_blocks = etherscan_blocks - ALERT_BLOCK_DIFFERENCE

    if (bitcore_blocks < alert_etherscan_blocks) or (parity_blocks < alert_etherscan_blocks):
        logging.info('%s New Alert status' % str(datetime.now()))
        send_to_all(generate_alert_message(sync_status))
        return True

    return False


def save_status_info(status_info):
    now = int(datetime.now().timestamp())
    if status_info:
        status_core = {'last_blocks_update': now, 'last_error': now}
    else:
        status_core = get_from_status_core()
        status_core['last_blocks_update'] = now
        if status_core['last_error']

    save_update_status_core_common(status_core)


def run_notifier():
    logging.info('Notifier launched')
    while True:
        sync_status = get_sync_status()
        status_info = is_current_status_alert(sync_status)
        save_status_info(status_info)

        sleep(3 * 60)


if __name__ == '__main__':
    run_notifier()
