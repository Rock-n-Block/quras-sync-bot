import psycopg2

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


def save_user_to_db(chat_id):
    conn = create_db_connection()
    cur = conn.cursor()
    existing_user = find_user_in_db(cur, chat_id)

    if not existing_user:
        cur.execute('INSERT INTO users (telegram_chat_id) VALUES (%s) ' % chat_id)
        conn.commit()

        print('user with id %s added to subscribe' % chat_id, flush=True)

    cur.close()
    conn.close()


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


def get_all_users():
    conn = create_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT telegram_chat_id FROM users;')
    res = cur.fetchall()

    cur.close()
    conn.close()

    users = [row[0] for row in res]

    return users


def save_update_block_cache(block_info):
    conn = create_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT id FROM last_blocks;')
    res = cur.fetchall()

    if len(res) > 0:
        sql_str = 'UPDATE last_blocks SET etherscan = {etherscan}, parity = {parity}, bitcore = {bitcore} WHERE id = 1'\
            .format(etherscan=block_info['etherscan'],
                    parity=block_info['parity'],
                    bitcore=block_info['bitcore']
                    )
    else:
        sql_str = 'INSERT INTO last_blocks (etherscan, parity, bitcore) VALUES ({etherscan}, {parity}, {bitcore})'\
            .format(etherscan=block_info['etherscan'],
                    parity=block_info['parity'],
                    bitcore=block_info['bitcore']
                    )

    # print(sql_str, flush=True)
    cur.execute(sql_str)
    conn.commit()

    cur.close()
    conn.close()

    print('Block cache updated', flush=True)


def get_from_block_cache():
    conn = create_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT etherscan, parity, bitcore FROM last_blocks WHERE id = 1;')
    res = cur.fetchall()
    row = res[0]

    block_cache = {
        'etherscan': row[0],
        'parity': row[1],
        'bitcore': row[2]
    }

    cur.close()
    conn.close()

    return block_cache

