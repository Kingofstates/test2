import os
import random
import string
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
RENDER_URL = "https://test2-1o72.onrender.com"

DATA_FILE = "users.txt"

app = Flask(__name__)

def generate_token(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def save_user(token, chat_id):
    with open(DATA_FILE, "a") as f:
        f.write(f"{token}:{chat_id}\n")

def find_chat_id(token):
    if not os.path.exists(DATA_FILE):
        return None
    with open(DATA_FILE, "r") as f:
        for line in f:
            t, chat_id = line.strip().split(":")
            if t == token:
                return chat_id
    return None

@app.route("/visit", methods=["POST"])
def visit():
    token = request.json.get("token")
    chat_id = find_chat_id(token)

    if chat_id:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id,
            "text": "Your webpage was opened ✔️"
        })
        return {"status": "sent"}

    return {"status": "invalid"}

application = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    token = generate_token()
    save_user(token, chat_id)

    link = f"https://kingofstates.github.io/test/?id={token}"
    await context.bot.send_message(chat_id=chat_id, text=f"Your private link:\n{link}")

application.add_handler(CommandHandler("start", start))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "Bot is running ✔️"

if __name__ == "__main__":
    application.bot.set_webhook(f"{RENDER_URL}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=10000)
