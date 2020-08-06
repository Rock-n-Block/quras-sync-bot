import psycopg2
import logging
import datetime

import settings


def create_db_connection():
    connection = psycopg2.connect(
        user=settings.POSTGRES_AUTH['user'],
        password=settings.POSTGRES_AUTH['password'],
        host=settings.POSTGRES_AUTH['host'],
        port=settings.POSTGRES_AUTH['port'],
        database=settings.POSTGRES_AUTH['database']
    )

    return connection


def initialize_common_table(sql_string):
    conn = create_db_connection()
    cur = conn.cursor()
    cur.execute(sql_string)
    conn.commit()
    cur.close()
    conn.close()


def initialize_user_table():
    initialize_common_table('CREATE TABLE users (id serial PRIMARY KEY, telegram_chat_id integer);')
    return


def initialize_blocks_table():
    sql_string = 'CREATE TABLE last_blocks (id serial PRIMARY KEY, etherscan integer, parity integer, bitcore integer);'
    initialize_common_table(sql_string)
    return


def initialize_status_core_table():
    sql_string = 'CREATE TABLE status_core (id serial PRIMARY KEY, last_blocks_update integer, last_error integer);'
    initialize_common_table(sql_string)
    return


def save_user_to_db(chat_id):
    conn = create_db_connection()
    cur = conn.cursor()

    new_user = False
    user = find_user_in_db(cur, chat_id)

    if not user:
        new_user = True
        cur.execute('INSERT INTO users (telegram_chat_id) VALUES (%s) ' % chat_id)
        conn.commit()

        logging.info('user with id %s added to subscribe' % chat_id,)

    cur.close()
    conn.close()

    return new_user


def find_user_in_db(cursor, chat_id):
    cursor.execute('SELECT telegram_chat_id FROM users WHERE telegram_chat_id = %s;' % chat_id)
    res = cursor.fetchall()

    user = None if len(res) == 0 else res[0][0]
    return user


def get_user_from_db(chat_id):
    conn = create_db_connection()
    cur = conn.cursor()

    user = find_user_in_db(cur, chat_id)
    cur.close()
    conn.close()
    return user


def delete_user_from_db(chat_id):
    conn = create_db_connection()
    cur = conn.cursor()

    user = find_user_in_db(cur, chat_id)

    if user:
        cur.execute('DELETE FROM users WHERE telegram_chat_id = %s;' % chat_id)
        conn.commit()

        logging.info('user with id %s deleted from subscription' % chat_id)

    cur.close()
    conn.close()


def get_all_users():
    conn = create_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT telegram_chat_id FROM users;')
    res = cur.fetchall()

    cur.close()
    conn.close()

    users = [row[0] for row in res]

    return users


def save_update_common(db, update_str, insert_str):
    conn = create_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT id FROM %s' % db)
    res = cur.fetchall()

    if len(res) > 0:
        sql_str = update_str
    else:
        sql_str = insert_str

    cur.execute(sql_str)
    conn.commit()

    cur.close()
    conn.close()


def save_update_block_cache(block_info):
    sql_update = 'UPDATE last_blocks SET etherscan = {etherscan}, parity = {parity}, bitcore = {bitcore} WHERE id = 1' \
        .format(etherscan=block_info['etherscan'],
                parity=block_info['parity'],
                bitcore=block_info['bitcore']
                )
    sql_insert = 'INSERT INTO last_blocks (etherscan, parity, bitcore) VALUES ({etherscan}, {parity}, {bitcore})'\
        .format(etherscan=block_info['etherscan'],
                parity=block_info['parity'],
                bitcore=block_info['bitcore']
                )

    save_update_common('last_blocks', sql_update, sql_insert)
    logging.info('Block cache updated')


def save_update_status_core_common(status_core):
    sql_update = 'UPDATE status_core SET last_blocks_update = {last_update}, last_error = {last_error} WHERE id = 1' \
        .format(last_update=status_core['last_blocks_update'], last_error=status_core["last_error"])
    sql_insert = 'INSERT INTO status_core  (last_blocks_update, last_error) VALUES ({last_update}, {last_error})' \
        .format(last_update=status_core['last_blocks_update'], last_error=status_core["last_error"])

    save_update_common('status_core', sql_update, sql_insert)
    logging.info('Status core updated')


# def save_update_block_cache(block_info):
#     conn = create_db_connection()
#     cur = conn.cursor()
#
#     cur.execute('SELECT id FROM last_blocks;')
#     res = cur.fetchall()
#
#     if len(res) > 0:
#         sql_str = 'UPDATE last_blocks SET etherscan = {etherscan}, parity = {parity}, bitcore = {bitcore} WHERE id = 1'\
#             .format(etherscan=block_info['etherscan'],
#                     parity=block_info['parity'],
#                     bitcore=block_info['bitcore']
#                     )
#     else:
#         sql_str = 'INSERT INTO last_blocks (etherscan, parity, bitcore) VALUES ({etherscan}, {parity}, {bitcore})'\
#             .format(etherscan=block_info['etherscan'],
#                     parity=block_info['parity'],
#                     bitcore=block_info['bitcore']
#                     )
#
#     cur.execute(sql_str)
#     conn.commit()
#
#     cur.close()
#     conn.close()
#
#     logging.info('Block cache updated')


def get_from_common(sql_str):
    conn = create_db_connection()
    cur = conn.cursor()

    cur.execute(sql_str)
    res = cur.fetchall()

    cur.close()
    conn.close()

    return res


def get_from_block_cache():
    block_cache_sql = 'SELECT etherscan, parity, bitcore FROM last_blocks WHERE id = 1;'
    db_result = get_from_common(block_cache_sql)
    row = db_result[0]

    block_cache = {
        'etherscan': row[0],
        'parity': row[1],
        'bitcore': row[2]
    }

    return block_cache


def get_from_status_core():
    status_core_sql = 'SELECT last_blocks_update, last_error FROM status_core WHERE id = 1;'
    db_result = get_from_common(status_core_sql)
