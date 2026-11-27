import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from flask import Flask
import threading

# --- TOKEN ---
TOKEN = os.environ.get("TOKEN") or "9263175788:AAEpjhIejWuvNSZr_2r4NtiTZJrRlbiKbjY"
ADMIN_ID = 123456789  # SHYIRAMO ID YAWE HANO

# --- Kugira ngo Render itazima ---
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot irimo gukora!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
threading.Thread(target=run_flask, daemon=True).start()

# --- Kubika abakoresha ---
user_states = {}  # {user_id: "kubikuza" cyangwa "link" cyangwa None}
active_links = {} # {user_id: True} kubuza link 2

def main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🚀 Tangira Gukora")],
        [KeyboardButton("💸 Kubikuza")],
        [KeyboardButton("❌ Hagarika")]
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # IYO AKANDITSE /start, MUREKURE MU BYO YARI ARIMO
    user_states[user_id] = None
    await update.message.reply_text(
        "Muraho! Murakaza neza kuri Korarwana Bot 🎉\n\nHitamo icyo ushaka gukora:",
        reply_markup=main_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # 1. NIBA AKANDITSE BOUTON, BANZA MUREKURE MU KUBIKUZA
    if text == "🚀 Tangira Gukora":
        user_states[user_id] = None  # <-- IYI NIYO FIX
        # Reba niba afite link itararangira
        if user_id in active_links:
            await update.message.reply_text("⚠️ Ufite link itararangira! RWabonye neza ikibazo. Ibyo ni uko bot yabaga igifashe ko uri kwandika nimero, ntikakurekure.

Nayikosoye. Ubu iyo ukanditse bouton iyo ari yo yose, cyangwa `/start`, cyangwa **❌ Hagarika**, ahita akurekura.

**Simbuza code yose muri GitHub n'iyi nshya:**

```python
import os, threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("TOKEN") or "SHYIRAMO_TOKEN_YAWE_HANO"
ADMIN_ID = 123456789  # SHYIRAMO ID YAWE

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot irimo gukora!"
def run_flask():
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()

user_states = {}
active_links = {}

def kb():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🚀 Tangira Gukora")],
        [KeyboardButton("💸 Kubikuza")],
        [KeyboardButton("❌ Hagarika")]
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = None  # Murekure
    await update.message.reply_text("Muraho! Murakaza neza 🎉\nHitamo:", reply_markup=kb())

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # --- FIX NYAMUKURU: Iyo akanditse bouton, murekure ---
    if text in ["🚀 Tangira Gukora", "💸 Kubikuza", "❌ Hagarika", "/start"]:
        user_states[user_id] = None

    if text == "❌ Hagarika":
        await update.message.reply_text("Byahagaritswe ✅. Hitamo ikindi:", reply_markup=kb())
        return

    if text == "🚀 Tangira Gukora":
        if user_id in active_links:
            await update.message.reply_text("⚠️ Ufite link itararangira! Rangiza iya mbere.")
            return
        active_links[user_id] = True
        await update.message.reply_text("✅ Link yawe: https://t.me/korarwana_bot?start=123\nYohereze ku nshuti zawe!")
        try:
            await context.bot.send_message(ADMIN_ID, f"Umuntu {user_id} yasabye link")
        except: pass
        return

    if text == "💸 Kubikuza":
        user_states[user_id] = "kubikuza"
        await update.message.reply_text("Andika nimero yo kubikuzaho (imibare gusa):\nNiba wibeshye, kanda ❌ Hagarika")
        return

    # Niba ari mu mode yo kubikuza
    if user_states.get(user_id) == "kubikuza":
        if not text.isdigit():
            await update.message.reply_text("❌ Andika imibare gusa! Urugero: 0781234567\nNiba ushaka kuva hano, kanda ❌ Hagarika")
            return
        user_states[user_id] = None
        await update.message.reply_text(f"✅ Nimero {text} yakiriwe! Kubikuza kurimo gukorwa...", reply_markup=kb())
        try:
            await context.bot.send_message(ADMIN_ID, f"Umuntu {user_id} akeneye kubikuza kuri: {text}")
        except: pass
        return

    await update.message.reply_text("Hitamo kuri bouton:", reply_markup=kb())

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("Bot irimo gukora...")
    app.run_polling()
