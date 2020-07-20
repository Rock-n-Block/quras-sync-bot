import telebot
import psycopg2

from status_fetcher import get_sync_status
import settings

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)


def create_db_connection():
    connection = psycopg2.connect(
        user=settings.POSTGRES_AUTH['user'],
        password=settings.POSTGRES_AUTH['password'],
        host=settings.POSTGRES_AUTH['host'],
        port=settings.POSTGRES_AUTH['port'],
        database=settings.POSTGRES_AUTH['database']
    )

    return connection


def initialize_user_table():
    conn = create_db_connection()
    cur = conn.cursor()
    cur.execute('CREATE TABLE users (id serial PRIMARY KEY, telegram_chat_id integer);')
    conn.commit()
    cur.close()
    conn.close()


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


def send_to_all(message):
    for user in get_all_users():
        bot.send_message(chat_id=user, text=message)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user_to_db(message.chat.id)


@bot.message_handler(commands=['ping'])
def send_pong(message):
    print('ping received, sending pong', flush=True)
    bot.send_message(message.chat.id, text='pong')


@bot.message_handler(commands=['status'])
def send_current_stats(message):
    current_status = get_sync_status()
    status_list = []
    for key, val in current_status.items():
        status_list.append('{source}: {blocks}'.format(source=key.upper(), blocks=val))
    status_text = '\n'.join(status_list)
    bot.send_message(message.chat.id, text=str(status_text))


if __name__ == '__main__':
    bot.polling()
