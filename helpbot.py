import telebot
from collections import defaultdict, deque
import threading
import time

TOKEN = '7298955377:AAERBmimaPqOPTEPBfqhfBB6IcetrVZeMb4'
bot = telebot.TeleBot(TOKEN)

user_contents = defaultdict(lambda: deque(maxlen=5))
user_message_ids = defaultdict(lambda: deque(maxlen=5))
user_locked = defaultdict(bool)
user_warns = defaultdict(int)

MAX_WARNS = 3
LOCK_TIME = 5

@bot.message_handler(content_types=['text', 'sticker'])
def handle_all_messages(message):
    if message.chat.type not in ['group', 'supergroup']:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    msg_id = message.message_id

    if message.content_type == 'text':
        content = f"text:{message.text.strip().lower()}"
    elif message.content_type == 'sticker':
        content = f"sticker:{message.sticker.file_unique_id}"
    else:
        return

    if user_locked[user_id]:
        return

    user_contents[user_id].append(content)
    user_message_ids[user_id].append(msg_id)

    if len(user_contents[user_id]) == 5 and len(set(user_contents[user_id])) == 1:
        for mid in list(user_message_ids[user_id]):
            try:
                bot.delete_message(chat_id, mid)
            except:
                pass

        user_warns[user_id] += 1
        warns = user_warns[user_id]
        username = message.from_user.username or message.from_user.first_name

        if warns >= MAX_WARNS:
            bot.send_message(chat_id, f"🚫 @{username}, у вас {warns} варнов. Вы заблокированы.")
            try:
                bot.ban_chat_member(chat_id, user_id)
            except:
                pass
            user_locked[user_id] = True
            threading.Thread(target=unlock_user, args=(user_id,)).start()
        else:
            bot.send_message(chat_id, f"⚠️ @{username}, предупреждение за спам. Варны: {warns}/{MAX_WARNS}")
            user_locked[user_id] = True
            threading.Thread(target=unlock_user, args=(user_id,)).start()

        user_contents[user_id].clear()
        user_message_ids[user_id].clear()

    if message.content_type == 'text':
        text = message.text.lower().strip()

        if 'http://' in text or 'https://' in text or 't.me/' in text:
            try:
                bot.delete_message(chat_id, msg_id)
                bot.send_message(chat_id, f"🚫 @{message.from_user.username}, в чате запрещены ссылки.")
                return
            except:
                return

        if 'Бот привет' in text:
            bot.reply_to(message, "Здраствуй мабой, 👋")
        elif 'Бот как дела' in text:
            bot.reply_to(message, "Норм, сам как? 😎")
        elif 'Бот что делаешь' in text:
            bot.reply_to(message, "Слежу за чатом 👀")
        elif 'Бот спишь' in text:
            bot.reply_to(message, "Боты не спят 😴")
        elif 'Бот кто ты' in text:
            bot.reply_to(message, "Я бот, твой защитник от спама 🤖")
        elif 'бот' in text and 'тупой' in text:
            bot.reply_to(message, "Сам ты такой 😤")
        elif 'Бот спасибо' in text:
            bot.reply_to(message, "Всегда пожалуйста 😊")
        elif 'Бот инфа' in text:
            bot.reply_to(message, "Я бот-помощник для этого чата, мои создатели: @noname_genius и @jnnnnnjj")
        elif 'Бот что ты умеешь' in text:
            bot.reply_to(message, "Я умею следить за чатом, общаться)")
        elif text == 'Гигачад':
            bot.reply_to(message, "Я тут")

def unlock_user(user_id):
    time.sleep(LOCK_TIME)
    user_locked[user_id] = False

bot.polling(none_stop=True)