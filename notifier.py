from datetime import datetime
from time import sleep
import logging

from status_fetcher import get_sync_status
from sync_bot import bot, send_to_all

from settings import ALERT_BLOCK_DIFFERENCE


def is_current_status_alert():
    sync_status = get_sync_status()

    etherscan_blocks = sync_status['etherscan']
    parity_blocks = sync_status['parity']
    bitcore_blocks = sync_status['bitcore']

    logging.info(sync_status)

    # etherscan_blocks += 55
    alert_etherscan_blocks = etherscan_blocks - ALERT_BLOCK_DIFFERENCE

    if (bitcore_blocks < alert_etherscan_blocks) or (parity_blocks < alert_etherscan_blocks):
        logging.info('%s New Alert status' % str(datetime.now()), flush=True)
        send_to_all(generate_alert_message(sync_status))
        return True

    return False


def generate_alert_message(current_status):
    status_list = []
    for key, val in current_status.items():
        status_list.append('{source}: {blocks}'.format(source=key.upper(), blocks=val))
    status_text = '\n'.join(status_list)
    alert_text = 'ALERT! Difference is deterministic! \n \n' + status_text
    return alert_text


def run_notifier():
    while True:
        logging.info('Notifier launched')
        is_current_status_alert()
        sleep(60)


if __name__ == '__main__':
    run_notifier()
