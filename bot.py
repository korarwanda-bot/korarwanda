import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# --- Kugira ngo Render itazima ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")
    def log_message(self, *args):
        pass
def run_web():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
threading.Thread(target=run_web, daemon=True).start()

TOKEN = os.environ.get("TOKEN") or "9263175788:AAEpjhIejWuvNSZr_2r4NtiTZJrRlbiKbjY"
BOT_USERNAME = "korarwana_bot"
ADMIN_ID = 8987587944

WHATSAPP_NUMBER = "0735966886"
WHATSAPP_LINK = "https://wa.me/250735966886"

ADMIN_AVAILABLE = True
ADMIN_RETURN_TIME = "14:00"
waiting_reply = {}
waiting_link_for = {}
user_balances = {}
user_names = {}

# --- KUBIKUZA ---
pending_withdraw = {}
waiting_withdraw_amount = {}
waiting_withdraw_number = {}

# --- NSHYA: LINK - KUBUZA GUSABA KABIRI ---
pending_link = {}  # user_id -> "waiting_admin" cyangwa "link_sent"

def get_balance(user_id):
    return user_balances.get(user_id, 0)
def add_money(user_id, amount):
    user_balances[user_id] = get_balance(user_id) + amount
    return user_balances[user_id]

def get_admin_status():
    if ADMIN_AVAILABLE:
        return "🟢 ADMIN ARIHO UBU\nYohereza link vuba. Kanda Tangira Gukora ubu."
    else:
        return f"🔴 ADMIN NTAHARI UBU\nAzagaruka: Saa {ADMIN_RETURN_TIME}\nSubiza nyuma y'icyo gihe, cyangwa wandikire kuri WhatsApp: {WHATSAPP_NUMBER}"

WELCOME_TEXT = """
👋 Murakaza neza!

Iyi bot igenewe umuntu wese ushaka gukorera amafaranga akaba afite telephone nshyashya itarafungurwaho email nyinshi cyangwa akaba afite sim card nshyashya.

Uko bikorwa:
Shyira sim card nshyashya muri telephone, fungura link uhabwa, verifying, nyuma garuka wemeze ko wakoze ibisabwa, tegereza uhabwe amafaranga yawe.

Uko gukorera amafaranga: Fungura link muri telephone irimo sim card nshyashya.

Niba uri umu agent muri iyi bot wayikoreraho amafaranga 200 kuri buri sim card ubaruye.

Kandi watumira umuntu ukinjiza 20 kuri buri sim imwe akoreye, ni ukuvuga ko gukorera 10 kwinjiza ayo uwo watumiye yinjije.

Aba agent bakorera amafaranga menshi.

Wemerewe kubikuza kuri Airtel cyangwa MTN.
"""

def get_main_menu():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🚀 Tangira Gukora")],
            [KeyboardButton("💰 Amafaranga Yanjye"), KeyboardButton("🤝 Tumira Inshuti")],
            [KeyboardButton("💸 Kubikuza"), KeyboardButton("❓ Ubufasha")],
            [KeyboardButton("🕐 Admin Ariho?")]
        ],
        resize_keyboard=True, one_time_keyboard=False, is_persistent=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_names[user.id] = user.first_name
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 UMUNTU MUSHYA!\n\n👤 {user.first_name}\n🆔 ID: {user.id}\n📱 @{user.username}")
    except: pass
    await update.message.reply_text(f"Muraho {user.first_name} 👋\n\n" + WELCOME_TEXT + f"\n\n{get_admin_status()}\n\n👇 MENU IRI HASI AHO:", reply_markup=get_main_menu())

async def ndahari_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_AVAILABLE
    if update.effective_user.id != ADMIN_ID: return
    ADMIN_AVAILABLE = True
    await update.message.reply_text("✅ Sawa! Ubu bot igaragaza ko URIHO.")

async def ntahari_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_AVAILABLE, ADMIN_RETURN_TIME
    if update.effective_user.id != ADMIN_ID: return
    if context.args:
        ADMIN_RETURN_TIME = context.args[0]
    ADMIN_AVAILABLE = False
    await update.message.reply_text(f"✅ Sawa! Ubu bot igaragaza ko NTAHARI. Uzagaruka saa {ADMIN_RETURN_TIME}.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    # --- CANCEL LINK ---
    if data == "cancel_link":
        if user.id in pending_link:
            pending_link.pop(user.id)
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"❌ {user.first_name} ({user.id}) YACANCELIZE GUSABA LINK.")
            await query.message.reply_text("✅ Gusaba link kwawe kwacancelizwe. Ubu ushobora gusaba indi.", reply_markup=get_main_menu())
        return

    if data == "check_withdraw":
        if user.id not in pending_withdraw:
            await query.message.reply_text("Nta kubikuza usabye ubu.", reply_markup=get_main_menu())
            return
        info = pending_withdraw[user.id]
        kb = [[InlineKeyboardButton("✅ EMEZA - WOHEREJE", callback_data=f"approve_wd_{user.id}"), InlineKeyboardButton("❌ OYA", callback_data=f"reject_wd_{user.id}")]]
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔍 {user.first_name} (@{user.username} | {user.id}) YAKANZE CHECKING!\n\n💸 Asabye kubikuza: {info['amount']} Rwf\n📱 Numero: {info['number']}\n💰 Balance ye: {get_balance(user.id)} Rwf\n\nUramwemeza?", reply_markup=InlineKeyboardMarkup(kb))
        await query.message.reply_text("Sawa! Wohereje Checking. Tegereza Admin akugenzure. ⏳", reply_markup=get_main_menu())
        return

    if data == "cancel_withdraw":
        if user.id in pending_withdraw:
            info =
