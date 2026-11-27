import os, threading, json, time
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("TOKEN") or "9263175788:AAEpjhIejWuvNSZr_2r4NtiTZJrRlbiKbjY"
ADMIN_ID = 123456789
BONUS_TUMIRA = 1000
BONUS_WATUMIWE = 500

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot irimo gukora!"
def run_flask():
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()

FILE = "balances.json"
def load_data():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r") as f: return json.load(f)
        except: pass
    return {"balances": {}, "invited": [], "kubikuza_done": {}}
def save_data():
    with open(FILE, "w") as f: json.dump(data, f)

data = load_data()
if "kubikuza_done" not in data:
    data["kubikuza_done"] = {}
user_states = {}
active_links = {}
pending_kubikuza = {}  # {user_id: amount} - ari gutegereza
last_kubikuza_time = {}  # kubuza spam

def get_balance(user_id):
    return data["balances"].get(str(user_id), 0)
def add_balance(user_id, amount):
    uid = str(user_id)
    data["balances"][uid] = get_balance(user_id) + amount
    save_data()

def kb_main():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🚀 Tangira Gukora")],
        [KeyboardButton("💰 Amafaranga Yanjye"), KeyboardButton("💸 Kubikuza")],
        [KeyboardButton("✅ Narangije Link"), KeyboardButton("❌ Hagarika")]
    ], resize_keyboard=True)

def kb_back():
    return ReplyKeyboardMarkup([[KeyboardButton("⬅️ Subira Inyuma")]], resize_keyboard=True)

def kb_confirm():
    return ReplyKeyboardMarkup([
        [KeyboardButton("✅ Yego, Bikuza"), KeyboardButton("❌ Cancel")],
    ], resize_keyboard=True)

def murekure(user_id):
    user_states[user_id] = None
    if user_id in pending_kubikuza:
        del pending_kubikuza[user_id]

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
                await context.bot.send_message(inviter, f"🎉 Watumiye umuntu! Wahawe {BONUS_TUMIRA} Rwf. Ufite ubu: {get_balance(inviter)} Rwf")
            except: pass
            await update.message.reply_text(f"🎉 Wakiriwe! Wahawe {BONUS_WATUMIWE} Rwf.\nAmafaranga yawe: {get_balance(user_id)} Rwf", reply_markup=kb_main())
            return
    await update.message.reply_text(f"Muraho! Murakaza neza 🎉\nAmafaranga yawe: {get_balance(user_id)} Rwf\nHitamo:", reply_markup=kb_main())

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip() if update.message.text else ""

    if text == "⬅️ Subira Inyuma":
        murekure(user_id)
        await update.message.reply_text(f"⬅️ Wasubiye kuri Menu.\nAmafaranga yawe: {get_balance(user_id)} Rwf", reply_markup=kb_main())
        return

    if text in ["❌ Hagarika", "❌ Cancel"]:
        was_pending = user_id in pending_kubikuza
        had_link = user_id in active_links
        if had_link: del active_links[user_id]
        murekure(user_id)
        if was_pending:
            await update.message.reply_text(f"❌ Kubikuza byahagaritswe.\nNta mafaranga yakuweho. Ufite: {get_balance(user_id)} Rwf", reply_markup=kb_main())
        elif had_link:
            await update.message.reply_text(f"❌ Link yahagaritswe. Ufite: {get_balance(user_id)} Rwf", reply_markup=kb_main())
        else:
            await update.message.reply_text("Byahagaritswe ✅.", reply_markup=kb_main())
        return

    # --- YEGO BIKUZA: UBWENGE BWO KUBUZA KABIRI ---
    if text == "✅ Yego, Bikuza":
        if user_id not in pending_kubikuza:
            await update.message.reply_text("Nta kubikuza gutegereje.", reply_markup=kb_main())
            return
        amount = pending_kubikuza[user_id]
        bal = get_balance(user_id)
        # 1. Niba amafaranga yagabanutse hagati aho
        if amount > bal:
            murekure(user_id)
            await update.message.reply_text(f"❌ Ufite {bal} Rwf gusa. Ntushobora kubikuza {amount} Rwf.", reply_markup=kb_main())
            return
        # 2. Niba yasabye vuba cyane (spam - munsi y'iminota 1)
        now = time.time()
        if user_id in last_kubikuza_time and (now - last_kubikuza_time[user_id]) < 60:
            await update.message.reply_text("⏳ Tegereza gato, kubikuza kwawe kurimo gukorwa. Ntushobora kubikuza kabiri icyarimwe.", reply_markup=kb_main())
            return
        # BIZIMA: Kura amafaranga, wandike ko yabikuje, funga
        data["balances"][str(user_id)] = bal - amount
        # Bika ko yabikuje - ntabwo ashobora kubikuza uwo mubare ukundi ako kanya
        if str(user_id) not in data["kubikuza_done"]:
            data["kubikuza_done"][str(user_id)] = []
        data["kubikuza_done"][str(user_id)].append({"amount": amount, "time": now})
        save_data()
        last_kubikuza_time[user_id] = now
        murekure(user_id)
        await update.message.reply_text(f"✅ Wabikuje {amount} Rwf!\nHasigaye: {get_balance(user_id)} Rwf\nAmafaranga yawe asigaye aragumaho, ntushobora kuyabikuza kabiri.", reply_markup=kb_main())
        try: await context.bot.send_message(ADMIN_ID, f"💸 Kubikuza: {user_id} yabikuje {amount} Rwf. Hasigaye {get_balance(user_id)} Rwf")
        except: pass
        return

    if text in ["🚀 Tangira Gukora", "💸 Kubikuza", "💰 Amafaranga Yanjye", "✅ Narangije Link", "/start"]:
        # Niba afite kubikuza gutegereje, ntimurekure ngo asabe ukundi
        if user_id not in pending_kubikuza:
            murekure(user_id)

    if text == "✅ Narangije Link":
        if user_id in active_links:
            del active_links[user_id]
            await update.message.reply_text("✅ Link yarangije. Ushobora gusaba indi.", reply_markup=kb_main())
        else:
            await update.message.reply_text("Nta link ufite.", reply_markup=kb_main())
        return

    if text == "💰 Amafaranga Yanjye":
        await update.message.reply_text(f"💰 Amafaranga yawe: {get_balance(user_id)} Rwf\nAragumaho kugeza uyabikuje rimwe.", reply_markup=kb_main())
        return

    if text == "🚀 Tangira Gukora":
        if user_id in active_links:
            await update.message.reply_text("⚠️ Ufite link itararangira!", reply_markup=kb_main())
            return
        active_links[user_id] = True
        link = f"https://t.me/korarwana_bot?start=ref_{user_id}"
        await update.message.reply_text(f"✅ Link yawe:\n{link}\n\nYohereze ku nshuti. Iyo umuntu yinjiye, wowe ubona {BONUS_TUMIRA} Rwf, na we abona {BONUS_WATUMIWE} Rwf.\nAmafaranga yawe ubu: {get_balance(user_id)} Rwf", reply_markup=kb_back())
        return

    if text == "💸 Kubikuza":
        # UBWENGE 1: Niba afite kubikuza gutegereje, mubwire
        if user_id in pending_kubikuza:
            await update.message.reply_text(f"⚠️ Ufite kubikuza gutegereje kwa {pending_kubikuza[user_id]} Rwf.\nEmeza cyangwa Cancel mbere yo gusaba ukundi.", reply_markup=kb_confirm())
            return
        # UBWENGE 2: Niba yasabye vuba cyane, mubwire ategereze
        now = time.time()
        if user_id in last_kubikuza_time and (now - last_kubikuza_time[user_id]) < 60:
            await update.message.reply_text(f"⏳ Kubikuza kwawe kurimo gukorwa. Tegereza iminota 1 mbere yo gusaba ukundi.\nUfite: {get_balance(user_id)} Rwf", reply_markup=kb_main())
            return
        if get_balance(user_id) <= 0:
            await update.message.reply_text(f"❌ Nta mafaranga ufite. Amafaranga yawe: 0 Rwf", reply_markup=kb_main())
            return
        user_states[user_id] = "kubikuza"
        await update.message.reply_text(f"Ufite: {get_balance(user_id)} Rwf\nAndika umubare ushaka kubikuza:", reply_markup=kb_back())
        return

    if user_states.get(user_id) == "kubikuza":
        if not text.isdigit():
            await update.message.reply_text("❌ Andika imibare gusa!", reply_markup=kb_back())
            return
        amount = int(text)
        bal = get_balance(user_id)
        if amount > bal:
            await update.message.reply_text(f"❌ Ufite {bal} Rwf gusa.", reply_markup=kb_back())
            return
        if amount <= 0:
            await update.message.reply_text("❌ Andika umubare urenze 0.", reply_markup=kb_back())
            return
        pending_kubikuza[user_id] = amount
        user_states[user_id] = "emeza"
        await update.message.reply_text(f"Ushaka kubikuza {amount} Rwf?\nHasigara {bal - amount} Rwf.\nKanda Yego cyangwa Cancel:", reply_markup=kb_confirm())
        return

    await update.message.reply_text("Hitamo kuri bouton:", reply_markup=kb_main())

async def handle_non_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    murekure(update.effective_user.id)
    await update.message.reply_text("Hitamo kuri bouton:", reply_markup=kb_main())

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VOICE | filters.STICKER | filters.Document.ALL, handle_non_text))
    print("Bot irimo gukora...")
    app.run_polling()
