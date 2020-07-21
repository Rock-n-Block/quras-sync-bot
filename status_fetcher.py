import requests
from datetime import datetime, timezone
import json
import logging

from database_api import save_update_block_cache, get_from_block_cache

import settings


class CommonFetchException(Exception):
    pass


class EtherscanFetchExecption(CommonFetchException):
    pass


class ParityFetchException(CommonFetchException):
    pass


class BitcoreFetchException(CommonFetchException):
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
        raise EtherscanFetchExecption()

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
        raise ParityFetchException()

    return res


def get_bitcore_status():
    url = 'https://quras-bitcore.rocknblock.io/api/ETH/mainnet/block/tip'
    json_headers = {"Content-Type": "application/json"}

    try:
        req = requests.get(url, headers=json_headers)
        res = json.loads(req.content)['height']
    except:
        raise BitcoreFetchException()

    return res


def get_sync_status():
    cached_services = []
    cached_values = get_from_block_cache()

    try:
        etherscan_value = get_etherscan_status()
    except EtherscanFetchExecption:
        etherscan_value = cached_values['etherscan']
        cached_services.append('etherscan')

    try:
        parity_value = get_parity_status()
    except ParityFetchException:
        parity_value = cached_values['parity']
        cached_services.append('parity')

    try:
        bitcore_value = get_bitcore_status()
    except EtherscanFetchExecption:
        bitcore_value = cached_values['bitcore']
        cached_services.append('bitcore')

    result = {
        'etherscan': etherscan_value,
        'parity': parity_value,
        'bitcore': bitcore_value,
    }
    save_update_block_cache(result)
    result['cached'] =  cached_services if len(cached_services) > 0 else False

    return result


def status_to_text(current_status):
    cache = current_status.pop('cached')

    status_list = []
    for key, val in current_status.items():
        status_list.append('{source}: {blocks}'.format(source=key.upper(), blocks=val))
    status_text = '\n'.join(status_list)

    if cache:
        cache_text = '\n\nWARNING: Could not retrieve information from: {cache_list}. Current values taken from cache' \
            .format(cache_list=', '.join([service.upper() for service in cache]))
        status_text += cache_text

    return status_text
