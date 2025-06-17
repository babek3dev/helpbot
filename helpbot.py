import telebot
from collections import defaultdict, deque
import threading
import time



TOKEN = '7298955377:AAERBmimaPqOPTEPBfqhfBB6IcetrVZeMb4'
bot = telebot.TeleBot(TOKEN)


# 🔹 Главный обработчик сообщений
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.chat.type not in ['group', 'supergroup']:
        return

    text = message.text.lower()

    # 1. Удаление рекламы (ссылки)
    if 'http://' in text or 'https://' in text or 't.me/' in text:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f"🚫 @{message.from_user.username},в чате запрещены ссылки.")
            return
        except:
            return

    # 2. Приветствие
    if 'привет' in text:
        bot.reply_to(message, f"Здраствуй мабой, 👋")
        
    # Ответы на простые фразы
    elif 'как дела' in text:
        bot.reply_to(message, "Норм, сам как? 😎")

    elif 'что делаешь' in text:
        bot.reply_to(message, "Слежу за чатом 👀")

    elif 'спишь' in text:
        bot.reply_to(message, "Боты не спят 😴")

    elif 'кто ты' in text:
        bot.reply_to(message, "Я бот, твой защитник от спама 🤖")

    elif 'бот' in text and 'тупой' in text:
        bot.reply_to(message, "Сам ты такой 😤")

    elif 'спасибо' in text:
        bot.reply_to(message, "Всегда пожалуйста 😊")
    elif 'инфа' in text:
        bot.reply_to(message, "Я бот-помощник для этого чата мои создатели : @noname_genius и @jnnnnnjj")
    elif 'что ты умеешь' in text:
        bot.reply_to(message, "Я умею следить за чатом,общатся)")
    elif 'бот' in text:
        bot.reply_to(message, "Я тут")    
        
                
user_contents = defaultdict(lambda: deque(maxlen=5))
user_message_ids = defaultdict(lambda: deque(maxlen=5))
user_locked = defaultdict(bool)
user_warns = defaultdict(int)  # счетчик варнов

MAX_WARNS = 3  # сколько варнов даем до бана или действия
LOCK_TIME = 5  # время блокировки после варна, сек

@bot.message_handler(content_types=['text', 'sticker'])
def handle_message(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    msg_id = message.message_id

    if message.content_type == 'text':
        content = f"text:{message.text}"
    elif message.content_type == 'sticker':
        content = f"sticker:{message.sticker.file_unique_id}"
    else:
        return

    if user_locked[user_id]:
        return

    user_contents[user_id].append(content)
    user_message_ids[user_id].append(msg_id)

    # Проверяем спам (5 одинаковых подряд сообщений)
    if len(user_contents[user_id]) == 5 and len(set(user_contents[user_id])) == 1:
        # Удаляем все последние 5 сообщений пользователя
        for mid in list(user_message_ids[user_id]):
            try:
                bot.delete_message(chat_id, mid)
            except Exception as e:
                pass

        # Добавляем варн
        user_warns[user_id] += 1
        warns = user_warns[user_id]

        username = message.from_user.username or message.from_user.first_name

        if warns >= MAX_WARNS:
            # Действие при достижении максимума варнов
            bot.send_message(chat_id, f"🚫 @{username}, у вас {warns} варнов. Вы заблокированы.")
            bot.ban_chat_member(message.chat.id, message.from_user.id)
            # Тут можно забанить пользователя, если у бота есть права:
            # bot.kick_chat_member(chat_id, user_id)
            # Или просто заблокировать на время
            user_locked[user_id] = True
            threading.Thread(target=unlock_user, args=(user_id,)).start()
        else:
            bot.send_message(chat_id, f"⚠️ @{username}, предупреждение за спам. Варны: {warns}/{MAX_WARNS}")
            user_locked[user_id] = True
            threading.Thread(target=unlock_user, args=(user_id,)).start()

        user_contents[user_id].clear()
        user_message_ids[user_id].clear()

def unlock_user(user_id):
    time.sleep(1)
    user_locked[user_id] = False

bot.polling(none_stop=True)