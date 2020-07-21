import requests
from datetime import datetime, timezone
import json

from database_api import save_update_block_cache, get_from_block_cache

import settings


class CommonFetchException(Exception):
    pass


def get_etherscan_status():
    url = 'https://api.etherscan.io/api'
    params = {
        'module': 'block',
        'action': 'getblocknobytime',
        'timestamp': int(datetime.now(timezone.utc).timestamp()),
        'closest': 'before',
        'apikey': settings.ETHERSCAN_TOKEN
    }
    try:
        req = requests.get(url, params)
        res = int(json.loads(req.content)['result'])
    except:
        raise CommonFetchException()

    return res


def get_parity_status():
    jsonrpc_url = 'http://{ip}:{port}'.format(ip=settings.PARITY_IP, port=settings.PARITY_PORT)
    jsonrpc_headers = {"Content-Type": "application/json"}
    method_call = 'eth_blockNumber'
    method_params = []

    data = {
        "jsonrpc": "2.0",
        "method": method_call,
        "params": method_params,
        "id": 1
    }

    try:
        req = requests.post(jsonrpc_url, headers=jsonrpc_headers, json=data)
        res = int(req.json()['result'], 16)
    except:
        raise CommonFetchException()

    return res


def get_bitcore_status():
    url = 'https://quras-bitcore.rocknblock.io/api/ETH/mainnet/block/tip'
    json_headers = {"Content-Type": "application/json"}

    try:
        req = requests.get(url, headers=json_headers)
        res = json.loads(req.content)['height']
    except:
        raise CommonFetchException()

    return res


def get_sync_status():
    try:
        result = {
            'etherscan': get_etherscan_status(),
            'parity': get_parity_status(),
            'bitcore': get_bitcore_status()
        }

        save_update_block_cache(result)
    except CommonFetchException:
        print('Error in fetching new blocks, retry in 60s', flush=True)
        result = get_from_block_cache()

    return result
