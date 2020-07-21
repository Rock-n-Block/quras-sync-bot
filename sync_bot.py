import telebot

from status_fetcher import get_sync_status
from database_api import save_user_to_db, get_all_users
import settings

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)


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
