import os, threading, json, time, re
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
pending_kubikuza = {}
last_kubikuza_time = {}

def get_balance(user_id):
    return data["balances"].get(str(user_id), 0)
def add_balance(user_id, amount):
    uid = str(user_id)
    data["balances"][uid] = get_balance(user_id) + amount
    save_data()

# BOUTON ZAWE NKUKO ZIRI MURI SCREENSHOT
def kb_main():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🚀 Tangira Gukora")],
        [KeyboardButton("💰 Amafaranga Yanjye"), KeyboardButton("🤝 Tumira Inshuti")],
        [KeyboardButton("💸 Kubikuza"), KeyboardButton("❓ Ubufasha")],
        [KeyboardButton("🕒 Admin Ariho?")]
    ], resize_keyboard=True)

def kb_back():
    return ReplyKeyboardMarkup([[KeyboardButton("⬅️ Subira Inyuma")]], resize_keyboard=True)

def kb_confirm():
    return ReplyKeyboardMarkup([
        [KeyboardButton("✅ Yego, Bikuza"), KeyboardButton("❌ Cancel")],
    ], resize_keyboard=True)

def kb_cancel():
    return ReplyKeyboardMarkup([[KeyboardButton("❌ Cancel")]], resize_keyboard=True)

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

    # === 1. BOUTON BURI GIHE ZIBANZA - NTIYIFATWA NKA NUMERO ===
    # Iki ni igisubizo: niba yanditse bouton, tuyikore, ntiyivuge ngo numero siyo
    BOUTONS = ["🚀 Tangira Gukora", "💰 Amafaranga Yanjye", "🤝 Tumira Inshuti", "💸 Kubikuza", "❓ Ubufasha", "🕒 Admin Ariho?", "⬅️ Subira Inyuma", "❌ Hagarika", "❌ Cancel", "✅ Yego, Bikuza", "✅ Narangije Link"]
    is_bouton = text in BOUTONS

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

    # Niba ari bouton, suka state ya numero / kubikuza mbere
    if is_bouton and user_id in pending_kubikuza and text != "✅ Yego, Bikuza":
        # Niba yakandye bouton indi mu gihe ategereje kwemeza, murekure
        if text not in ["✅ Yego, Bikuza"]:
            pass

    if text == "✅ Yego, Bikuza":
        if user_id not in pending_kubikuza:
            await update.message.reply_text("Nta kubikuza gutegereje.", reply_markup=kb_main())
            return
        amount = pending_kubikuza[user_id]
        bal = get_balance(user_id)
        if amount > bal:
            murekure(user_id)
            await update.message.reply_text(f"❌ Ufite {bal} Rwf gusa.", reply_markup=kb_main())
            return
        now = time.time()
        if user_id in last_kubikuza_time and (now - last_kubikuza_time[user_id]) < 60:
            await update.message.reply_text("⏳ Tegereza gato, kubikuza kwawe kurimo gukorwa. Ntushobora kubikuza kabiri icyarimwe.", reply_markup=kb_main())
            return
        # Ubu saba numero - amafaranga NTARAVAHO
        user_states[user_id] = "numero"
        await update.message.reply_text(f"✅ Ushaka kubikuza {amount} Rwf.\n\nUbu andika numero yawe ya MTN/Airtel gusa, imibare gusa:\nUrugero: 0781234567", reply_markup=kb_cancel())
        return

    # === 2. BOUTON Z'IBANZA ===
    if text == "💰 Amafaranga Yanjye":
        murekure(user_id)
        await update.message.reply_text(f"💰 Amafaranga yawe: {get_balance(user_id)} Rwf", reply_markup=kb_main())
        return

    if text == "🤝 Tumira Inshuti":
        murekure(user_id)
        link = f"https://t.me/korarwana_bot?start=ref_{user_id}"
        await update.message.reply_text(f"🤝 Link yawe yo gutumira:\n{link}\n\nYohereze ku nshuti. Iyo umuntu yinjiye, wowe ubona {BONUS_TUMIRA} Rwf, na we abona {BONUS_WATUMIWE} Rwf.", reply_markup=kb_main())
        return

    if text == "🚀 Tangira Gukora":
        murekure(user_id)
        if user_id in active_links:
            await update.message.reply_text("⚠️ Ufite link itararangira!", reply_markup=kb_main())
            return
        active_links[user_id] = True
        link = f"https://t.me/korarwana_bot?start=ref_{user_id}"
        await update.message.reply_text(f"✅ Link yawe:\n{link}\n\nYohereze ku nshuti. Iyo umuntu yinjiye, wowe ubona {BONUS_TUMIRA} Rwf.", reply_markup=kb_main())
        return

    if text == "✅ Narangije Link":
        if user_id in active_links:
            del active_links[user_id]
            await update.message.reply_text("✅ Link yarangije. Ushobora gusaba indi.", reply_markup=kb_main())
        else:
            await update.message.reply_text("Nta link ufite.", reply_markup=kb_main())
        return

    if text == "❓ Ubufasha":
        murekure(user_id)
        await update.message.reply_text("❓ Ubufasha:\n- Tangira Gukora: ubona link yo gutumira\n- Tumira Inshuti: ubona link\n- Kubikuza: ukura amafaranga yawe\n- Andika numero itangira na 07, imibare 10", reply_markup=kb_main())
        return

    if text == "🕒 Admin Ariho?":
        murekure(user_id)
        await update.message.reply_text("🕒 Admin ariho. Andika ikibazo cyawe, azakusubiza vuba.", reply_markup=kb_main())
        return

    if text == "💸 Kubikuza":
        if user_id in pending_kubikuza:
            await update.message.reply_text(f"⚠️ Ufite kubikuza gutegereje kwa {pending_kubikuza[user_id]} Rwf.\nEmeza cyangwa Cancel mbere yo gusaba ukundi.", reply_markup=kb_confirm())
            return
        now = time.time()
        if user_id in last_kubikuza_time and (now - last_kubikuza_time[user_id]) < 60:
            await update.message.reply_text(f"⏳ Kubikuza kwawe kurimo gukorwa. Tegereza iminota 1.\nUfite: {get_balance(user_id)} Rwf", reply_markup=kb_main())
            return
        if get_balance(user_id) <= 0:
            await update.message.reply_text(f"❌ Nta mafaranga ufite. Amafaranga yawe: 0 Rwf", reply_markup=kb_main())
            return
        user_states[user_id] = "kubikuza"
        await update.message.reply_text(f"Ufite: {get_balance(user_id)} Rwf\nAndika umubare ushaka kubikuza:", reply_markup=kb_back())
        return

    # === 3. NUMERO - GUSA NIBA ATARI BOUTON ===
    if user_states.get(user_id) == "numero" and not is_bouton:
        # Sukura numero: suka espace, +250, -
        numero = text.replace(" ", "").replace("-", "").replace("+250", "0")
        # Reba niba ari imibare 10 itangira na 07
        if not re.fullmatch(r"07\d{8}", numero):
            await update.message.reply_text("⚠️ Oya! Numero siyo.\n\nAndika numero y'imibare 10 gusa itangira na 07.\nUrugero: 0781234567", reply_markup=kb_cancel())
            return
        # NUMERO NIYO - UBU NIBWO AMAFARANGA AVAHO
        amount = pending_kubikuza.get(user_id, 0)
        bal = get_balance(user_id)
        if amount > bal:
            murekure(user_id)
            await update.message.reply_text(f"❌ Ufite {bal} Rwf gusa.", reply_markup=kb_main())
            return
        data["balances"][str(user_id)] = bal - amount
        if str(user_id) not in data["kubikuza_done"]:
            data["kubikuza_done"][str(user_id)] = []
        data["kubikuza_done"][str(user_id)].append({"amount": amount, "numero": numero, "time": time.time()})
        save_data()
        last_kubikuza_time[user_id] = time.time()
        murekure(user_id)
        await update.message.reply_text(f"✅ Wabikuje {amount} Rwf kuri {numero}!\nHasigaye: {get_balance(user_id)} Rwf\nAmafaranga azakugeraho vuba.", reply_markup=kb_main())
        try: await context.bot.send_message(ADMIN_ID, f"💸 Kubikuza: {user_id} yabikuje {amount} Rwf kuri {numero}. Hasigaye {get_balance(user_id)} Rwf")
        except: pass
        return

    # === 4. UMUBARE WO KUBIKUZA ===
    if user_states.get(user_id) == "kubikuza" and not is_bouton:
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
    app.add_handler(MessageHandler(filters.PHOTO | filters.VOICE | filters.Sticker.ALL | filters.Document.ALL, handle_non_text))
    print("Bot irimo gukora...")
    app.run_polling()
