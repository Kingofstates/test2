import os
import random
import string
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("8335451744:AAFdHaNTmePzoznm4nf81nHCKiUpi7zG0kA")
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    token = generate_token()
    save_user(token, chat_id)

    link = f"https://kingofstates.github.io/test/?id={token}"
    await context.bot.send_message(chat_id=chat_id, text=f"Your private link:\n{link}")

def run_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.run_polling()

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)
