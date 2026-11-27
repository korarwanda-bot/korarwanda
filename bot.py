import os, threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("TOKEN") or "9263175788:AAEpjhIejWuvNSZr_2r4NtiTZJrRlbiKbjY"
ADMIN_ID = 123456789  # SHYIRAMO ID YAWE

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot irimo gukora!"
def run_flask():
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()

user_states = {}
active_links = {}

# --- MENU NKURU ---
def kb_main():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🚀 Tangira Gukora")],
        [KeyboardButton("💸 Kubikuza")],
        [KeyboardButton("✅ Narangije Link"), KeyboardButton("❌ Hagarika")]
    ], resize_keyboard=True)

# --- MENU YO GUSUBIRA INYUMA ---
def kb_back():
    return ReplyKeyboardMarkup([
        [KeyboardButton("⬅️ Subira Inyuma")]
    ], resize_keyboard=True)

def murekure(user_id):
    user_states[user_id] = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    murekure(user_id)
    await update.message.reply_text("Muraho! Murakaza neza 🎉\nHitamo:", reply_markup=kb_main())

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip() if update.message.text else ""

    # --- BOUTON YO GUSUBIRA INYUMA ---
    if text == "⬅️ Subira Inyuma":
        murekure(user_id)
        await update.message.reply_text("⬅️ Wasubiye kuri Menu nkuru.\nHitamo icyo ushaka gukora:", reply_markup=kb_main())
        return

    # Iyo akanditse bouton nkuru, murekure
    if text in ["🚀 Tangira Gukora", "💸 Kubikuza", "✅ Narangije Link", "❌ Hagarika", "/start"]:
        murekure(user_id)

    if text == "❌ Hagarika":
        if user_id in active_links:
            del active_links[user_id]
        await update.message.reply_text("Byahagaritswe ✅.", reply_markup=kb_main())
        return

    if text == "✅ Narangije Link":
        if user_id in active_links:
            del active_links[user_id]
            await update.message.reply_text("✅ Link yarangije. Ubu ushobora gusaba indi.", reply_markup=kb_main())
        else:
            await update.message.reply_text("Nta link ufite itararangira.", reply_markup=kb_main())
        return

    if text == "🚀 Tangira Gukora":
        if user_id in active_links:
            await update.message.reply_text("⚠️ Ufite link itararangira! Kanda ✅ Narangije Link.", reply_markup=kb_main())
            return
        active_links[user_id] = True
        # Iyo amaze gusaba link, mumwereke bouton yo gusubira inyuma
        await update.message.reply_text("✅ Link yawe: https://t.me/korarwana_bot?start=123\nNimara kuyikoresha kanda ✅ Narangije Link", reply_markup=kb_back())
        try: await context.bot.send_message(ADMIN_ID, f"Umuntu {user_id} yasabye link")
        except: pass
        return

    if text == "💸 Kubikuza":
        user_states[user_id] = "kubikuza"
        # Iyo ari kwandika nimero, mumwereke bouton yo gusubira inyuma
        await update.message.reply_text("Andika nimero (imibare gusa):\nNiba wibeshye kanda ⬅️ Subira Inyuma", reply_markup=kb_back())
        return

    if user_states.get(user_id) == "kubikuza":
        if not text.isdigit():
            await update.message.reply_text("❌ Andika imibare gusa! Urugero: 0781234567\nKanda ⬅️ Subira Inyuma niba ushaka kuva hano", reply_markup=kb_back())
            return
        user_states[user_id] = None
        await update.message.reply_text(f"✅ Nimero {text} yakiriwe!", reply_markup=kb_main())
        try: await context.bot.send_message(ADMIN_ID, f"Kubikuza: {user_id} -> {text}")
        except: pass
        return

    await update.message.reply_text("Hitamo kuri bouton:", reply_markup=kb_main())

async def handle_non_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    murekure(user_id)
    await update.message.reply_text("Wohereze ubutumwa bw'inyandiko. Hitamo:", reply_markup=kb_main())

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VOICE | filters.STICKER | filters.Document.ALL, handle_non_text))
    print("Bot irimo gukora...")
    app.run_polling()
