import telebot
from collections import defaultdict
import time
import threading
import re

TOKEN = '7298955377:AAERBmimaPqOPTEPBfqhfBB6IcetrVZeMb4
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

SPAM_INTERVAL = 1.0  # интервал между сообщениями (сек)
MAX_WARNS = 3

last_message_time = defaultdict(float)
user_warns = defaultdict(int)

# регулярка для ссылок
link_regex = re.compile(
    r'(?i)(https?://|www\.|t\.me/|telegram\.me/|tg://|discord\.gg/|'
    r'\b[a-z0-9\-_]+\.(ru|su|com|net|org|info|biz|io|me|gg|ly|xyz|top|app)\b)'
)

@bot.message_handler(content_types=['text', 'sticker','gif'])
def handle_message(message):
    if message.chat.type not in ('group', 'supergroup'):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    msg_id = message.message_id
    key = (chat_id, user_id)
    now = time.time()

    elapsed = now - last_message_time[key]
    last_message_time[key] = now

    # Удаляем, если отправлено слишком быстро после предыдущего
    if elapsed < SPAM_INTERVAL:
        threading.Thread(target=try_delete, args=(chat_id, msg_id)).start()
        warn_user(chat_id, user_id, message.from_user)
        return

    # Проверка на ссылки
    if message.content_type == 'text':
        text = message.text.lower()
        if link_regex.search(text):
            threading.Thread(target=try_delete, args=(chat_id, msg_id)).start()
            bot.send_message(chat_id, f"🚫 @{get_username(message.from_user)}, ссылки у нас запрещены.")
            return

        # Ответы бота
        if 'бот кто ты' in text:
            bot.reply_to(message, "Я Антиспам бот 🤖")
        elif 'бот привет' in text:
            bot.reply_to(message, "Здраствуй, мабой 👋")

def try_delete(chat_id, msg_id):
    try:
        bot.delete_message(chat_id, msg_id)
    except Exception as e:
        print(f"Ошибка удаления: {e}")

def warn_user(chat_id, user_id, user_obj):
    key = (chat_id, user_id)
    user_warns[key] += 1
    warns = user_warns[key]
    username = get_username(user_obj)

    if warns >= MAX_WARNS:
        bot.send_message(chat_id, f"🚫 @{username}, это третье предупреждение — бан.")
        try:
            bot.ban_chat_member(chat_id, user_id)
        except Exception as e:
            print(f"Ошибка бана: {e}")
        user_warns[key] = 0
    else:
        bot.send_message(chat_id,
                         f"⚠️ @{username}, не спамь. Варны: {warns}/{MAX_WARNS}")

def get_username(user):
    return user.username or user.first_name

bot.polling(none_stop=True, skip_pending=True)