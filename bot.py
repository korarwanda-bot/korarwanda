import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN ="9263175788:AAEpjhIejWuvNSZr_2r4NtiTZJrRlbiKbjY"
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
Uko bikorwa: Shyira sim card nshyashya muri telephone, fungura link uhabwa, verifying, nyuma garuka wemeze ko wakoze ibisabwa, tegereza uhabwe amafaranga yawe.
Uko gukorera amafaranga: Fungura link muri telephone irimo sim card nshyashya.
Niba uri umu agent muri iyi bot wayikoreraho amafaranga 200 kuri buri sim card ubaruye.
Kandi watumira umuntu ukinjiza 20 kuri buri sim imwe akoreye.
Wemerewe kubikuza kuri Airtel cyangwa MTN.
"""

def get_main_menu():
    return ReplyKeyboardMarkup([[KeyboardButton("🚀 Tangira Gukora")],[KeyboardButton("💰 Amafaranga Yanjye"), KeyboardButton("🤝 Tumira Inshuti")],[KeyboardButton("💸 Kubikuza"), KeyboardButton("❓ Ubufasha")],[KeyboardButton("🕐 Admin Ariho?")]], resize_keyboard=True, one_time_keyboard=False, is_persistent=True)

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
    if data == "check_done":
        keyboard = [[InlineKeyboardButton("✅ EMEZA +100 Rwf", callback_data=f"approve_work_{user.id}")],[InlineKeyboardButton("❌ OYA", callback_data=f"reject_work_{user.id}")]]
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔍 {user.first_name} (@{user.username} | {user.id}) AVUZE KO YAKOZE!\nBalance ye: {get_balance(user.id)} Rwf", reply_markup=InlineKeyboardMarkup(keyboard))
        await query.message.reply_text("Sawa! Wohereje ko wakoze. Tegereza Admin akugenzure. ⏳", reply_markup=get_main_menu())
        return
    if user.id != ADMIN_ID: return
    if data.startswith("write_link_"):
        target_id = int(data.split("_")[2])
        waiting_link_for[ADMIN_ID] = target_id
        await query.message.reply_text(f"✍️ Sawa! Andika LINK ushaka kohereza kuri {target_id} ubu:")
        return
    if data.startswith("approve_work_"):
        target_id = int(data.split("_")[2])
        new_balance = add_money(target_id, 100)
        name = user_names.get(target_id, "Umuntu")
        await context.bot.send_message(chat_id=target_id, text=f"🎉 CONGRATS {name}!\n\n✅ Wakorewe neza!\n💰 Wabonye: +100 Rwf\n💰 Balance yawe ubu: {new_balance} Rwf", reply_markup=get_main_menu())
        await query.message.reply_text(f"✅ Wemeje {target_id}! Yahawe 100. Balance: {new_balance}")
        return
    if data.startswith("reject_work_"):
        target_id = int(data.split("_")[2])
        await context.bot.send_message(chat_id=target_id, text="❌ Ntibyemejwe. Ongera ugerageze.", reply_markup=get_main_menu())
        await query.message.reply_text(f"❌ Wanze {target_id}")
        return
    if data.startswith("askreply_"):
        target_id = int(data.split("_")[1])
        waiting_reply[ADMIN_ID] = target_id
        await query.message.reply_text(f"✍️ Andika ubutumwa kuri {target_id}:")
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_names[user.id] = user.first_name
    if user.id == ADMIN_ID and ADMIN_ID in waiting_link_for:
        target_id = waiting_link_for.pop(ADMIN_ID)
        check_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ NAKOZE - CHECK ✔️", callback_data="check_done")]])
        await context.bot.send_message(chat_id=target_id, text=f"🔗 Dore link yo gukorera:\n\n{text}\n\n1. Fungura muri telephone irimo sim card nshya\n2. Kora verifying\n3. Nyuma ukande bouton hepfo 👇", reply_markup=check_keyboard)
        await update.message.reply_text(f"✅ Link yoherejwe kuri {target_id}!")
        return
    if user.id == ADMIN_ID and ADMIN_ID in waiting_reply:
        target_id = waiting_reply.pop(ADMIN_ID)
        await context.bot.send_message(chat_id=target_id, text=f"💬 Ubutumwa buvuye kuri Admin:\n\n{text}", reply_markup=get_main_menu())
        await update.message.reply_text(f"✅ Bwoherejwe kuri {target_id}")
        return
    if text == "🚀 Tangira Gukora":
        if not ADMIN_AVAILABLE:
            await update.message.reply_text(f"🔴 ADMIN NTAHARI UBU\n\nAzagaruka: Saa {ADMIN_RETURN_TIME}\nSubiza nyuma y'icyo gihe.\n\nCyamunara wandikire kuri WhatsApp: {WHATSAPP_NUMBER}", reply_markup=get_main_menu())
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"👀 {user.first_name} ({user.id}) Yaje gusaba link kandi NTAHARI. Azagaruka saa {ADMIN_RETURN_TIME}")
            return
        keyboard = [[InlineKeyboardButton("✍️ ANDIKA LINK UMUHE UBU", callback_data=f"write_link_{user.id}")],[InlineKeyboardButton("💬 Musubize", callback_data=f"askreply_{user.id}")]]
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🚀 {user.first_name} (@{user.username} | {user.id}) YASABYE LINK!", reply_markup=InlineKeyboardMarkup(keyboard))
        await update.message.reply_text("Sawa! Admin ariho ubu. Agiye kukwandikira link vuba. ⏳", reply_markup=get_main_menu())
        return
    if text == "🕐 Admin Ariho?":
        await update.message.reply_text(get_admin_status(), reply_markup=get_main_menu())
        return
    if text == "💰 Amafaranga Yanjye":
        await update.message.reply_text(f"💰 {user.first_name}, Balance yawe: {get_balance(user.id)} Rwf", reply_markup=get_main_menu())
        return
    if text == "🤝 Tumira Inshuti":
        invite_link = f"https://t.me/{BOT_USERNAME}?start={user.id}"
        await update.message.reply_text(f"Tumira inshuti:\n\n{invite_link}", reply_markup=get_main_menu())
        return
    if text == "💸 Kubikuza":
        bal = get_balance(user.id)
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"💸 {user.first_name} ({user.id}) YASABYE KUBIKUZA! Balance: {bal} Rwf")
        await update.message.reply_text(f"Balance yawe: {bal} Rwf\nAndika numero yawe ya MTN/Airtel:", reply_markup=get_main_menu())
        return
    if text == "❓ Ubufasha":
        help_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("💬 Andikira kuri WhatsApp", url=WHATSAPP_LINK)]])
        await update.message.reply_text(f"❓ UKENEYE UBUFASHA?\n\nWandikire kuri WhatsApp:\n\n📱 Nimero: {WHATSAPP_NUMBER}\n👇 Kanda bouton hepfo:", reply_markup=help_keyboard)
        return
    keyboard = [[InlineKeyboardButton("💬 Musubize", callback_data=f"askreply_{user.id}")], [InlineKeyboardButton("✍️ Andika Link", callback_data=f"write_link_{user.id}")]]
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"💬 UBUTUMWA!\nKuva: {user.first_name} (@{user.username} | {user.id})\nYanditse: {text}", reply_markup=InlineKeyboardMarkup(keyboard))
    await update.message.reply_text("Murakoze! Ubutumwa bwawe bwakiriwe. ✅", reply_markup=get_main_menu())

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ndahari", ndahari_command))
app.add_handler(CommandHandler("ntahari", ntahari_command))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
print("Bot irimo gukora...")
app.run_polling()
