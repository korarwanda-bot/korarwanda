import os, threading, json
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("TOKEN") or "9263175788:AAEpjhIejWuvNSZr_2r4NtiTZJrRlbiKbjY"
ADMIN_ID = 123456789
BONUS_TUMIRA = 1000
BONUS_WATUMIWE = 500

app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot irimo gukora!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

threading.Thread(target=run_flask, daemon=True).start()

FILE = "balances.json"

def load_data():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"balances": {}, "invited": []}

def save_data():
    with open(FILE, "w") as f:
        json.dump(data, f)

data = load_data()
user_states = {}
active_links = {}

def get_balance(user_id):
    return data["balances"].get(str(user_id), 0)

def add_balance(user_id, amount):
    uid = str(user_id)
    data["balances"][uid] = get_balance(user_id) + amount
    save_data()

def kb_main():
    return ReplyKeyboardMarkup([
        [KeyboardButton("Tangira Gukora")],
        [KeyboardButton("Amafaranga Yanjye"), KeyboardButton("Kubikuza")],
        [KeyboardButton("Narangije Link"), KeyboardButton("Hagarika")]
    ], resize_keyboard=True)

def kb_back():
    return ReplyKeyboardMarkup([[KeyboardButton("Subira Inyuma")]], resize_keyboard=True)

def murekure(user_id):
    user_states[user_id] = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    murekure(user_id)
    args = context.args
    if args and args[0].startswith("ref_"):
        inviter = args[0].replace("ref_", "")
        if inviter != str(user_id) and str(user_id) not in data["invited"]:
            data["invited"].append(str(user_id))
            add_balance(inviter, BONUS_TUMIRA)
            add_balance(user_id, BONUS_WATUMIWE)
            save_data()
            try:
                await context.bot.send_message(inviter, f"Watumiwe umuntu! Wahawe {BONUS_TUMIRA} Rwf. Ufite ubu: {get_balance(inviter)} Rwf")
            except:
                pass
            await update.message.reply_text(f"Wakiriwe! Wahawe {BONUS_WATUMIWE} Rwf yo kwakirwa. Amafaranga yawe: {get_balance(user_id)} Rwf", reply_markup=kb_main())
            return
    await update.message.reply_text(f"Muraho! Murakaza neza. Amafaranga yawe: {get_balance(user_id)} Rwf. Hitamo:", reply_markup=kb_main())

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip() if update.message.text else ""

    if text == "Subira Inyuma":
        murekure(user_id)
        await update.message.reply_text(f"Wasubiye kuri Menu. Amafaranga yawe: {get_balance(user_id)} Rwf", reply_markup=kb_main())
        return

    if text in ["Tangira Gukora", "Kubikuza", "Amafaranga Yanjye", "Narangije Link", "Hagarika", "/start"]:
        murekure(user_id)

    if text == "Hagarika":
        if user_id in active_links:
            del active_links[user_id]
        await update.message.reply_text("Byahagaritswe.", reply_markup=kb_main())
        return

    if text == "Narangije Link":
        if user_id in active_links:
            del active_links[user_id]
            await update.message.reply_text("Link yarangije. Ushobora gusaba indi.", reply_markup=kb_main())
        else:
            await update.message.reply_text("Nta link ufite.", reply_markup=kb_main())
        return

    if text == "Amafaranga Yanjye":
        await update.message.reply_text(f"Amafaranga yawe: {get_balance(user_id)} Rwf. Azagumaho kugeza uyabikuje.", reply_markup=kb_main())
        return

    if text == "Tangira Gukora":
        if user_id in active_links:
            await update.message.reply_text("Ufite link itararangira!", reply_markup=kb_main())
            return
        active_links[user_id] = True
        link = f"https://t.me/korarwana_bot?start=ref_{user_id}"
        await update.message.reply_text(f"Link yawe: {link} Yohereze ku nshuti. Iyo umuntu yinjiye, wowe ubona {BONUS_TUMIRA} Rwf, na we abona {BONUS_WATUMIWE} Rwf. Amafaranga yawe ubu: {get_balance(user_id)} Rwf", reply_markup=kb_back())
        return

    if text == "Kubikuza":
        if get_balance(user_id) <= 0:
            await update.message.reply_text(f"Nta mafaranga ufite. Amafaranga yawe: 0 Rwf. Tumira abantu ubone amafaranga.", reply_markup=kb_main())
            return
        user_states[user_id] = "kubikuza"
        await update.message.reply_text(f"Ufite: {get_balance(user_id)} Rwf. Andika umubare ushaka kubikuza (imibare gusa):", reply_markup=kb_back())
        return

    if user_states.get(user_id) == "kubikuza":
        if not text.isdigit():
            await update.message.reply_text("Andika imibare gusa!", reply_markup=kb_back())
            return
        amount = int(text)
        bal = get_balance(user_id)
        if amount > bal:
            await update.message.reply_text(f"Ufite {bal} Rwf gusa. Andika umubare uri munsi cyangwa ungana nawo.", reply_markup=kb_back())
            return
        if amount <= 0:
            await update.message.reply_text("Andika umubare urenze 0.", reply_markup=kb_back())
            return
        data["balances"][str(user_id)] = bal - amount
        save_data()
        user_states[user_id] = None
        await update.message.reply_text(f"Wabikuje {amount} Rwf! Hasigaye: {get_balance(user_id)} Rwf. Azakugeraho vuba.", reply_markup=kb_main())
        try:
            await context.bot.send_message(ADMIN_ID, f"Kubikuza: {user_id} yabikuje {amount} Rwf. Hasigaye {get_balance(user_id)} Rwf")
        except:
            pass
        return

    await update.message.reply_text("Hitamo kuri bouton:", reply_markup=kb_main())

async def handle_non_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    murekure(update.effective_user.id)
    await update.message.reply_text("Hitamo kuri bouton:", reply_markup=kb_main())

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VOICE | filters.Sticker.ALL | filters.Document.ALL, handle_non_text))
    print("Bot irimo gukora...")
    app.run_polling()
