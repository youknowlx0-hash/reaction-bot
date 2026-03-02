import telebot
import requests
import json
import os
from telebot import types

# ================= CONFIG =================
BOT_TOKEN = "8614118579:AAE4QhemihHCUj01dcRzGe138_8QEX0vmHo"

ADMIN_IDS = [6813806104]  # Apna Telegram numeric ID daalo
FORCE_CHANNEL = "@botsbylucky"  # Join karwana wala channel

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
USERS_FILE = "users.json"

# ================= USER DATABASE =================

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# ================= FORCE JOIN CHECK =================

def is_joined(user_id):
    try:
        member = bot.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def send_force_join(message):
    markup = types.InlineKeyboardMarkup()
    join_btn = types.InlineKeyboardButton(
        "📢 Join Channel",
        url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}"
    )
    check_btn = types.InlineKeyboardButton(
        "✅ Joined",
        callback_data="check_join"
    )
    markup.add(join_btn)
    markup.add(check_btn)

    bot.send_message(
        message.chat.id,
        "🚫 <b>Access Denied!</b>\n\nBot use karne ke liye pehle channel join karo.",
        reply_markup=markup
    )

# ================= AUTO REACTION =================

@bot.channel_post_handler(content_types=['text','photo','video'])
def auto_react(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction"

    data = {
        "chat_id": message.chat.id,
        "message_id": message.message_id,
        "reaction": [
            {"type": "emoji", "emoji": "🔥"}
        ]
    }

    requests.post(url, json=data)

# ================= START =================

@bot.message_handler(commands=['start'])
def start(message):

    if not is_joined(message.from_user.id):
        send_force_join(message)
        return

    users = load_users()
    if message.from_user.id not in users:
        users.append(message.from_user.id)
        save_users(users)

    bot.send_message(message.chat.id, "🔥 Bot Ready to Use!")

# ================= JOIN CHECK BUTTON =================

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_callback(call):

    if is_joined(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ Access Granted! Bot Ready.")
    else:
        bot.answer_callback_query(call.id, "❌ Abhi channel join nahi kiya.")

# ================= STATS (ADMIN ONLY) =================

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized.")
        return

    users = load_users()
    bot.reply_to(message, f"📊 Total Users: {len(users)}")

# ================= BROADCAST (ADMIN ONLY) =================

@bot.message_handler(commands=['broadcast'])
def broadcast(message):

    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized.")
        return

    text = message.text.replace("/broadcast ", "")

    if text == "/broadcast":
        bot.reply_to(message, "⚠️ Message do broadcast ke liye.")
        return

    users = load_users()
    sent = 0

    for user in users:
        try:
            bot.send_message(user, f"📢 {text}")
            sent += 1
        except:
            pass

    bot.reply_to(message, f"✅ Broadcast Sent to {sent} users.")

# ================= RUN =================

bot.delete_webhook()
print("Bot Running...")
bot.infinity_polling(skip_pending=True)
