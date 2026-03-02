import telebot
from telebot import types
import json
import os

# ================== CONFIG ==================
BOT_TOKEN = "8614118579:AAE4QhemihHCUj01dcRzGe138_8QEX0vmHo"
ADMIN_IDS = [6813806104]  # Yaha apna Telegram user ID daalo
FORCE_CHANNEL = "@BotsbyLucky"  # Apna channel username daalo

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

USERS_FILE = "users.json"

# ================== FILE SYSTEM ==================

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# ================== START ==================

@bot.message_handler(commands=['start'])
def start(message):
    users = load_users()
    if message.from_user.id not in users:
        users.append(message.from_user.id)
        save_users(users)

    bot.reply_to(message, 
        "🔥 <b>Welcome to Reaction Bot</b>\n\n"
        "This bot helps boost engagement.\n"
        "Add it to your channel/group and enjoy!"
    )

# ================== STATS (ADMIN ONLY) ==================

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized.")
        return

    users = load_users()
    bot.reply_to(message, 
        f"📊 <b>Bot Statistics</b>\n\n"
        f"👥 Total Users: {len(users)}"
    )

# ================== BROADCAST (ADMIN ONLY) ==================

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized.")
        return

    msg = message.text.replace("/broadcast ", "")

    if msg == "/broadcast":
        bot.reply_to(message, "⚠️ Please provide a message to broadcast.")
        return

    users = load_users()
    sent = 0
    failed = 0

    for user in users:
        try:
            bot.send_message(user, f"📢 <b>Broadcast Message</b>\n\n{msg}")
            sent += 1
        except:
            failed += 1

    bot.reply_to(message, 
        f"✅ Broadcast Completed\n\n"
        f"✔️ Sent: {sent}\n"
        f"❌ Failed: {failed}"
    )

# ================== RUN ==================
print("Removing webhook...")
bot.delete_webhook()

print("Bot is running...")
bot.infinity_polling()
