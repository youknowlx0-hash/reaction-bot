import telebot
from telebot import types
from flask import Flask, request
import json, os

TOKEN = "8614118579:AAE4QhemihHCUj01dcRzGe138_8QEX0vmHo"
FORCE_CHANNEL = "@BotsbyLucky"
OWNER_ID = 6813806104

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

DATA_FILE = "data.json"

# ---------------- DATA ----------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": [], "channels": [], "groups": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ---------------- FORCE JOIN ----------------
def is_joined(user_id):
    try:
        member = bot.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    data = load_data()

    if message.from_user.id not in data["users"]:
        data["users"].append(message.from_user.id)
        save_data(data)

    if not is_joined(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔔 Join Channel",
                    url=f"https://t.me/{FORCE_CHANNEL[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ I Joined",
                    callback_data="check_join"))

        bot.send_message(message.chat.id,
                         "⚠️ Pehle channel join karo.",
                         reply_markup=markup)
        return

    main_menu(message)

def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Add Your Channel", "➕ Add Your Group")
    if message.from_user.id == OWNER_ID:
        markup.add("📊 Bot Stats", "📢 Broadcast")
    bot.send_message(message.chat.id,
                     "🤖 Welcome! Choose option:",
                     reply_markup=markup)

# ---------------- CHECK JOIN BUTTON ----------------
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join_callback(call):
    if is_joined(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Verified!")
        main_menu(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Join first!")

# ---------------- ADD CHANNEL ----------------
@bot.message_handler(func=lambda m: m.text == "➕ Add Your Channel")
def add_channel(message):
    bot.send_message(message.chat.id,
                     "Channel me bot ko admin banao\nFir username bhejo (Example: @botsbylucky)

@bot.message_handler(func=lambda m: m.text and m.text.startswith("@"))
def save_channel(message):
    data = load_data()
    try:
        member = bot.get_chat_member(message.text, bot.get_me().id)
        if member.status in ["administrator", "creator"]:
            if message.text not in data["channels"]:
                data["channels"].append(message.text)
                save_data(data)
            bot.send_message(message.chat.id,
                             "✅ Channel Setted & Reaction Active 🔥")
        else:
            bot.send_message(message.chat.id,
                             "❌ Bot admin nahi hai us channel me.")
    except:
        pass

# ---------------- ADD GROUP ----------------
@bot.message_handler(func=lambda m: m.text == "➕ Add Your Group")
def add_group(message):
    bot.send_message(message.chat.id,
                     "Group me bot ko admin banao\nFir group me koi message bhejo.")

# ---------------- AUTO SAVE GROUP ----------------
@bot.message_handler(content_types=['new_chat_members'])
def auto_group_save(message):
    data = load_data()
    if message.chat.type in ["group", "supergroup"]:
        if bot.get_me().id in [u.id for u in message.new_chat_members]:
            if str(message.chat.id) not in data["groups"]:
                data["groups"].append(str(message.chat.id))
                save_data(data)
            bot.send_message(message.chat.id,
                             "✅ Group Setted & Reaction Active 🔥")

# ---------------- AUTO REACTION ----------------
@bot.message_handler(func=lambda m: True)
def auto_react(message):
    data = load_data()

    if message.chat.username and ("@" + message.chat.username) in data["channels"]:
        try:
            bot.set_message_reaction(
                message.chat.id,
                message.message_id,
                [types.ReactionTypeEmoji("🔥")]
            )
        except:
            pass

    if str(message.chat.id) in data["groups"]:
        try:
            bot.set_message_reaction(
                message.chat.id,
                message.message_id,
                [types.ReactionTypeEmoji("🔥")]
            )
        except:
            pass

# ---------------- OWNER PANEL ----------------
@bot.message_handler(func=lambda m: m.text == "📊 Bot Stats")
def stats(message):
    if message.from_user.id == OWNER_ID:
        data = load_data()
        bot.send_message(message.chat.id,
                         f"👥 Users: {len(data['users'])}\n"
                         f"📢 Channels: {len(data['channels'])}\n"
                         f"👥 Groups: {len(data['groups'])}")

@bot.message_handler(func=lambda m: m.text == "📢 Broadcast")
def broadcast_prompt(message):
    if message.from_user.id == OWNER_ID:
        msg = bot.send_message(message.chat.id,
                               "Send message to broadcast:")
        bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    data = load_data()
    count = 0
    for user in data["users"]:
        try:
            bot.send_message(user, message.text)
            count += 1
        except:
            pass
    bot.send_message(message.chat.id,
                     f"✅ Broadcast sent to {count} users.")

# ---------------- WEBHOOK ----------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot Running"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://reaction-bot-bl9e.onrender.com/8614118579:AAE4QhemihHCUj01dcRzGe138_8QEX0vmHo")
    app.run(host="0.0.0.0", port=10000)
