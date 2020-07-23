import telebot
import logging

from status_fetcher import get_sync_status, status_to_text
from database_api import save_user_to_db, get_all_users, delete_user_from_db
import settings

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
status_item = telebot.types.KeyboardButton('/status')
keyboard.row(status_item)


def send_to_all(message):
    for user in get_all_users():
        bot.send_message(chat_id=user, text=message)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    new_user = save_user_to_db(message.chat.id)
    if new_user:
        msg_text = "Great! You've beem added to subscribtion list and will receive alerts."
    else:
        msg_text = 'Already registered'

    bot.send_message(message.chat.id, text=msg_text, reply_markup=keyboard)


@bot.message_handler(commands=['ping'])
def send_pong(message):
    logging.info('ping received, sending pong')
    bot.send_message(message.chat.id, text='pong', reply_markup=keyboard)


@bot.message_handler(commands=['status'])
def send_current_stats(message):
    current_status = get_sync_status()
    # current_status.pop('cached')

    status_text = status_to_text(current_status)
    logging.info('status request received')
    bot.send_message(message.chat.id, text=str(status_text), reply_markup=keyboard)


@bot.message_handler(commands=['unsubscribe'])
def send_unsubscribe(message):
    delete_user_from_db(message.chat.id)
    msg_text = "You've been unsubcribed from alert. But you can still requests info with /status"
    bot.send_message(message.chat.id, text=msg_text, reply_markup=keyboard)


def run_bot():
    bot.polling()


if __name__ == '__main__':
    run_bot()
