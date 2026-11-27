import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton
from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram import KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.ext import CallbackQueryHandler, ContextTypes
from telegram.ext import MessageHandler, filters

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
pending_withdraw = {}
waiting_withdraw_amount = {}
waiting_withdraw_number = {}
pending_link = {}

def get_balance(user_id):
    return user_balances.get(user_id, 0)

def add_money(user_id, amount):
    user_balances[user_id] = get_balance(user_id) + amount
    return user_balances[user_id]

def get_admin_status():
    if ADMIN_AVAILABLE:
        return "🟢 ADMIN ARIHO UBU\nYohereza link vuba."
    else:
        return "🔴 ADMIN NTAHARI UBU\nAzagaruka: Saa " + ADMIN_RETURN_TIME

WELCOME_TEXT = "👋 Murakaza neza!\n\nIyi bot igenewe gukorera amafaranga.\nShyira sim card nshya muri telephone,\nfungura link uhabwa, verifying,\nnyuma garuka wemeze ko wakoze.\n\nWemerewe kubikuza kuri Airtel cyangwa MTN."

def get_main_menu():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🚀 Tangira Gukora")],
            [KeyboardButton("💰 Amafaranga Yanjye"),
             KeyboardButton("🤝 Tumira Inshuti")],
            [KeyboardButton("💸 Kubikuza"),
             KeyboardButton("❓ Ubufasha")],
            [KeyboardButton("🕐 Admin Ariho?")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True
    )

async def start(update, context):
    user = update.effective_user
    user_names[user.id] = user.first_name
    try:
        msg = "🔔 UMUNTU MUSHYA!\n\n"
        msg += user.first_name + "\n"
        msg += "ID: " + str(user.id)
        await context.bot.send_message(
            chat_id=ADMIN_ID, text=msg
        )
    except:
        pass
    txt = "Muraho " + user.first_name + " 👋\n\n"
    txt += WELCOME_TEXT + "\n\n"
    txt += get_admin_status()
    txt += "\n\n👇 MENU IRI HASI AHO:"
    await update.message.reply_text(
        txt, reply_markup=get_main_menu()
    )

async def ndahari_command(update, context):
    global ADMIN_AVAILABLE
    if update.effective_user.id != ADMIN_ID:
        return
    ADMIN_AVAILABLE = True
    await update.message.reply_text("✅ Sawa! Ubu bot igaragaza ko URIHO.")

async def ntahari_command(update, context):
    global ADMIN_AVAILABLE, ADMIN_RETURN_TIME
    if update.effective_user.id != ADMIN_ID:
        return
    if context.args:
        ADMIN_RETURN_TIME = context.args[0]
    ADMIN_AVAILABLE = False
    await update.message.reply_text("✅ Sawa! Ubu bot igaragaza ko NTAHARI.")

async def button(update, context):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    if data == "cancel_link":
        if user.id in pending_link:
            pending_link.pop(user.id)
            txt = "❌ " + user.first_name
            txt += " YACANCELIZE GUSABA LINK."
            await context.bot.send_message(
                chat_id=ADMIN_ID, text=txt
            )
            await query.message.reply_text(
                "✅ Gusaba link kwacancelizwe.",
                reply_markup=get_main_menu()
            )
        return

    if data == "check_withdraw":
        if user.id not in pending_withdraw:
            await query.message.reply_text(
                "Nta kubikuza usabye ubu.",
                reply_markup=get_main_menu()
            )
            return
        info = pending_withdraw[user.id]
        kb = [
            [InlineKeyboardButton(
                "✅ EMEZA - WOHEREJE",
                callback_data="approve_wd_" + str(user.id)
            ),
             InlineKeyboardButton(
                "❌ OYA",
                callback_data="reject_wd_" + str(user.id)
            )]
        ]
        txt = "🔍 " + user.first_name + " YAKANZE CHECKING!\n\n"
        txt += "Asabye: " + str(info["amount"]) + " Rwf\n"
        txt += "Numero: " + info["number"]
        await context.bot.send_message(
            chat_id=ADMIN_ID, text=txt,
            reply_markup=InlineKeyboardMarkup(kb)
        )
        await query.message.reply_text(
            "Sawa! Wohereje Checking. Tegereza Admin. ⏳",
            reply_markup=get_main_menu()
        )
        return

    if data == "cancel_withdraw":
        if user.id in pending_withdraw:
            info = pending_withdraw.pop(user.id)
            txt = "❌ " + user.first_name + " YACANCELIZE KUBIKUZA "
            txt += str(info["amount"]) + " Rwf."
            await context.bot.send_message(
                chat_id=ADMIN_ID, text=txt
            )
            await query.message.reply_text(
                "✅ Kubikuza kwacancelizwe.",
                reply_markup=get_main_menu()
            )
        return

    if data == "check_done":
        kb = [
            [InlineKeyboardButton(
                "✅ EMEZA +100 Rwf",
                callback_data="approve_work_" + str(user.id)
            )],
            [InlineKeyboardButton(
                "❌ OYA",
                callback_data="reject_work_" + str(user.id)
            )]
        ]
        txt = "🔍 " + user.first_name + " AVUZE KO YAKOZE!\n"
        txt += "Balance: " + str(get_balance(user.id))
        await context.bot.send_message(
            chat_id=ADMIN_ID, text=txt,
            reply_markup=InlineKeyboardMarkup(kb)
        )
        await query.message.reply_text(
            "Sawa! Wohereje ko wakoze. Tegereza Admin. ⏳",
            reply_markup=get_main_menu()
        )
        return

    if user.id != ADMIN_ID:
        return

    if data.startswith("approve_wd_"):
        target_id = int(data.split("_")[2])
        if target_id in pending_withdraw:
            info = pending_withdraw.pop(target_id)
            user_balances[target_id] = get_balance(target_id) - info["amount"]
            txt = "🎉 KUBIKUZA KWEMEJWE!\n\n"
            txt += "Woherejwe: " + str(info["amount"]) + " Rwf\n"
            txt += "Kuri: " + info["number"] + "\n"
            txt += "Hasigaye: " + str(get_balance(target_id))
            await context.bot.send_message(
                chat_id=target_id, text=txt,
                reply_markup=get_main_menu()
            )
            await query.message.reply_text("✅ Wemeje kubikuza.")
        return

    if data.startswith("reject_wd_"):
        target_id = int(data.split("_")[2])
        if target_id in pending_withdraw:
            info = pending_withdraw.pop(target_id)
            txt = "❌ Kubikuza kwawe kwa "
            txt += str(info["amount"]) + " Rwf ntikwemejwe."
            await context.bot.send_message(
                chat_id=target_id, text=txt,
                reply_markup=get_main_menu()
            )
            await query.message.reply_text("❌ Wanze kubikuza.")
        return

    if data.startswith("write_link_"):
        target_id = int(data.split("_")[2])
        waiting_link_for[ADMIN_ID] = target_id
        await query.message.reply_text(
            "✍️ Andika LINK ushaka kohereza ubu:"
        )
        return

    if data.startswith("approve_work_"):
        target_id = int(data.split("_")[2])
        if target_id in pending_link:
            pending_link.pop(target_id)
        new_balance = add_money(target_id, 100)
        name = user_names.get(target_id, "Umuntu")
        txt = "🎉 CONGRATS " + name + "!\n\n"
        txt += "✅ Wakorewe neza!\n"
        txt += "Wabonye: +100 Rwf\n"
        txt += "Balance: " + str(new_balance) + " Rwf"
        await context.bot.send_message(
            chat_id=target_id, text=txt,
            reply_markup=get_main_menu()
        )
        await query.message.reply_text("✅ Wemeje! Yahawe 100.")
        return

    if data.startswith("reject_work_"):
        target_id = int(data.split("_")[2])
        if target_id in pending_link:
            pending_link.pop(target_id)
        await context.bot.send_message(
            chat_id=target_id,
            text="❌ Ntibyemejwe. Ongera ugerageze.",
            reply_markup=get_main_menu()
        )
        await query.message.reply_text("❌ Wanze.")
        return

    if data.startswith("askreply_"):
        target_id = int(data.split("_")[1])
        waiting_reply[ADMIN_ID] = target_id
        await query.message.reply_text(
            "✍️ Andika ubutumwa ubu:"
        )
        return

async def handle_message(update, context):
    user = update.effective_user
    text = update.message.text.strip()
    user_names[user.id] = user.first_name

    if user.id == ADMIN_ID and ADMIN_ID in waiting_link_for:
        target_id = waiting_link_for.pop(ADMIN_ID)
        if target_id in pending_link:
            pending_link[target_id] = "link_sent"
        kb = [
            [InlineKeyboardButton(
                "✅ NAKOZE - CHECK ✔️",
                callback_data="check_done"
            )],
            [InlineKeyboardButton(
                "❌ CANCEL LINK",
                callback_data="cancel_link"
            )]
        ]
        txt = "🔗 Dore link yo gukorera:\n\n"
        txt += text + "\n\n"
        txt += "1. Fungura muri telephone irimo sim nshya\n"
        txt += "2. Kora verifying\n"
        txt += "3. Nyuma ukande bouton hepfo 👇"
        await context.bot.send_message(
            chat_id=target_id, text=txt,
            reply_markup=InlineKeyboardMarkup(kb)
        )
        await update.message.reply_text("✅ Link yoherejwe!")
        return

    if user.id == ADMIN_ID and ADMIN_ID in waiting_reply:
        target_id = waiting_reply.pop(ADMIN_ID)
        txt = "💬 Ubutumwa buvuye kuri Admin:\n\n" + text
        await context.bot.send_message(
            chat_id=target_id, text=txt,
            reply_markup=get_main_menu()
        )
        await update.message.reply_text("✅ Bwoherejwe.")
        return

    MAIN_BOUTONS = [
        "🚀 Tangira Gukora",
        "💰 Amafaranga Yanjye",
        "🤝 Tumira Inshuti",
        "💸 Kubikuza",
        "❓ Ubufasha",
        "🕐 Admin Ariho?"
    ]

    if text in MAIN_BOUTONS:
        if user.id in waiting_withdraw_amount:
            waiting_withdraw_amount.pop(user.id)
        if user.id in waiting_withdraw_number:
            waiting_withdraw_number.pop(user.id)

    if user.id in waiting_withdraw_amount:
        if text not in MAIN_BOUTONS:
            clean = text.replace("Rwf", "")
            clean = clean.replace("rwf", "")
            clean = clean.replace(",", "")
            clean = clean.replace(" ", "")
            clean = clean.strip()
            if not clean.isdigit():
                await update.message.reply_text(
                    "⚠️ Oya! Andika imibare gusa.\nUrugero: 5000",
                    reply_markup=get_main_menu()
                )
                return
            amount = int(clean)
            bal = get_balance(user.id)
            if amount <= 0:
                await update.message.reply_text(
                    "⚠️ Ingano igomba kuba irenze 0.",
                    reply_markup=get_main_menu()
                )
                return
            if amount > bal:
                txt = "❌ Ntabwo ufite ayo mafaranga!\n"
                txt += "Balance yawe: " + str(bal) + " Rwf"
                await update.message.reply_text(
                    txt, reply_markup=get_main_menu()
                )
                return
            waiting_withdraw_amount.pop(user.id)
            waiting_withdraw_number[user.id] = amount
            txt = "✅ Ushaka kubikuza " + str(amount) + " Rwf.\n\n"
            txt += "Ubu andika numero yawe ya MTN/Airtel gusa:\n"
            txt += "Urugero: 0781234567"
            await update.message.reply_text(
                txt, reply_markup=get_main_menu()
            )
            return

    if user.id in waiting_withdraw_number:
        if text not in MAIN_BOUTONS:
            clean_num = text.replace(" ", "")
            clean_num = clean_num.replace("+", "")
            clean_num = clean_num.replace("-", "")
            clean_num = clean_num.strip()
            if not clean_num.isdigit():
                await update.message.reply_text(
                    "⚠️ Oya! Numero siyo.\nAndika numero 10 itangira na 07.",
                    reply_markup=get_main_menu()
                )
                return
            if len(clean_num) != 10:
                await update.message.reply_text(
                    "⚠️ Oya! Numero siyo.\nAndika numero 10 itangira na 07.",
                    reply_markup=get_main_menu()
                )
                return
            if not clean_num.startswith("07"):
                await update.message.reply_text(
                    "⚠️ Oya! Numero siyo.\nAndika numero 10 itangira na 07.",
                    reply_markup=get_main_menu()
                )
                return
            amount = waiting_withdraw_number.pop(user.id)
            pending_withdraw[user.id] = {
                "amount": amount,
                "number": clean_num,
                "name": user.first_name
            }
            kb_admin = [
                [InlineKeyboardButton(
                    "✅ EMEZA",
                    callback_data="approve_wd_" + str(user.id)
                ),
                 InlineKeyboardButton(
                    "❌ OYA",
                    callback_data="reject_wd_" + str(user.id)
                )]
            ]
            txt = "💸 GUSABA KUBIKUZA GUSHYA!\n\n"
            txt += user.first_name + "\n"
            txt += "Ingano: " + str(amount) + " Rwf\n"
            txt += "Numero: " + clean_num
            await context.bot.send_message(
                chat_id=ADMIN_ID, text=txt,
                reply_markup=InlineKeyboardMarkup(kb_admin)
            )
            kb_user = [
                [InlineKeyboardButton(
                    "✅ CHECKING",
                    callback_data="check_withdraw"
                ),
                 InlineKeyboardButton(
                    "❌ CANCEL",
                    callback_data="cancel_withdraw"
                )]
            ]
            txt2 = "✅ Gusaba kwawe kwakiriwe!\n\n"
            txt2 += "Ingano: " + str(amount) + " Rwf\n"
            txt2 += "Numero: " + clean_num
            await update.message.reply_text(
                txt2, reply_markup=InlineKeyboardMarkup(kb_user)
            )
            return

    if text == "🚀 Tangira Gukora":
        if user.id in pending_link:
            status = pending_link[user.id]
            if status == "waiting_admin":
                kb = [
                    [InlineKeyboardButton(
                        "❌ CANCEL LINK",
                        callback_data="cancel_link"
                    )]
                ]
                await update.message.reply_text(
                    "⚠️ Ufite link usabye itararangira!",
                    reply_markup=InlineKeyboardMarkup(kb)
                )
                return
            if status == "link_sent":
                kb = [
                    [InlineKeyboardButton(
                        "✅ NAKOZE - CHECK ✔️",
                        callback_data="check_done"
                    )],
                    [InlineKeyboardButton(
                        "❌ CANCEL LINK",
                        callback_data="cancel_link"
                    )]
                ]
                await update.message.reply_text(
                    "⚠️ Ufite link itararangira!",
                    reply_markup=InlineKeyboardMarkup(kb)
                )
                return
        if not ADMIN_AVAILABLE:
            txt = "🔴 ADMIN NTAHARI UBU\n\n"
            txt += "Azagaruka: Saa " + ADMIN_RETURN_TIME
            await update.message.reply_text(
                txt, reply_markup=get_main_menu()
            )
            return
        pending_link[user.id] = "waiting_admin"
        kb = [
            [InlineKeyboardButton(
                "✍️ ANDIKA LINK UMUHE UBU",
                callback_data="write_link_" + str(user.id)
            )],
            [InlineKeyboardButton(
                "💬 Musubize",
                callback_data="askreply_" + str(user.id)
            )]
        ]
        txt = "🚀 " + user.first_name + " YASABYE LINK!"
        await context.bot.send_message(
            chat_id=ADMIN_ID, text=txt,
            reply_markup=InlineKeyboardMarkup(kb)
        )
        await update.message.reply_text(
            "Sawa! Admin ariho ubu. Agiye kukwandikira link vuba. ⏳",
            reply_markup=get_main_menu()
        )
        return

    if text == "🕐 Admin Ariho?":
        await update.message.reply_text(
            get_admin_status(),
            reply_markup=get_main_menu()
        )
        return

    if text == "💰 Amafaranga Yanjye":
        txt = "💰 " + user.first_name
        txt += ", Balance yawe: "
        txt += str(get_balance(user.id)) + " Rwf"
        await update.message.reply_text(
            txt, reply_markup=get_main_menu()
        )
        return

    if text == "🤝 Tumira Inshuti":
        invite_link = "https://t.me/" + BOT_USERNAME
        invite_link += "?start=" + str(user.id)
        await update.message.reply_text(
            "Tumira inshuti:\n\n" + invite_link,
            reply_markup=get_main_menu()
        )
        return

    if text == "💸 Kubikuza":
        if user.id in pending_withdraw:
            info = pending_withdraw[user.id]
            kb = [
                [InlineKeyboardButton(
                    "✅ CHECKING",
                    callback_data="check_withdraw"
                ),
                 InlineKeyboardButton(
                    "❌ CANCEL",
                    callback_data="cancel_withdraw"
                )]
            ]
            txt = "⚠️ Ufite kubikuza itararangira!\n\n"
            txt += "Ingano: " + str(info["amount"]) + " Rwf\n"
            txt += "Numero: " + info["number"]
            await update.message.reply_text(
                txt, reply_markup=InlineKeyboardMarkup(kb)
            )
            return
        bal = get_balance(user.id)
        if bal <= 0:
            await update.message.reply_text(
                "Balance yawe ni 0 Rwf. Banza ukore.",
                reply_markup=get_main_menu()
            )
            return
        waiting_withdraw_amount[user.id] = True
        txt = "💸 Balance yawe: " + str(bal) + " Rwf\n\n"
        txt += "Andika ingano ushaka kubikuza:\nUrugero: 5000"
        await update.message.reply_text(
            txt, reply_markup=get_main_menu()
        )
        return

    if text == "❓ Ubufasha":
        kb = [
            [InlineKeyboardButton(
                "💬 Andikira kuri WhatsApp",
                url=WHATSAPP_LINK
            )]
        ]
        txt = "❓ UKENEYE UBUFASHA?\n\n"
        txt += "WhatsApp: " + WHATSAPP_NUMBER
        await update.message.reply_text(
            txt, reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    kb = [
        [InlineKeyboardButton(
            "💬 Musubize",
            callback_data="askreply_" + str(user.id)
        )],
        [InlineKeyboardButton(
            "✍️ Andika Link",
            callback_data="write_link_" + str(user.id)
        )]
    ]
    txt = "💬 UBUTUMWA!\nKuva: " + user.first_name + "\n"
    txt += "Yanditse: "
