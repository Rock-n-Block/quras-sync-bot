from datetime import datetime
from time import sleep

from status_fetcher import get_sync_status
from sync_bot import bot, send_to_all

from settings import ALERT_BLOCK_DIFFERENCE


def is_current_status_alert():
    sync_status = get_sync_status()

    etherscan_blocks = sync_status['etherscan']
    parity_blocks = sync_status['parity']
    bitcore_blocks = sync_status['bitcore']

    for k, v in sync_status.items():
        print(k, v, flush=True)

    # etherscan_blocks += 55
    alert_etherscan_blocks = etherscan_blocks - ALERT_BLOCK_DIFFERENCE

    if (bitcore_blocks < alert_etherscan_blocks) or (parity_blocks < alert_etherscan_blocks):
        print('%s New Alert status' % str(datetime.now()), flush=True)
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


if __name__ == '__main__':
    while True:
        print('Notifier launched', flush=True)
        is_current_status_alert()
        sleep(60)
