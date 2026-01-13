import asyncio
import os
import time
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.filters import CommandStart

# ================= CONFIG =================

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 6734269605          # admin ID
ADMIN_USERNAME = "https://t.me/the_797"
CHANNEL_USERNAME = "@the7dvn"

ANTI_SPAM_SECONDS = 5         # 5 soniya

# ================= SQLITE =================

db = sqlite3.connect("bot.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    lang TEXT,
    last_msg REAL
)
""")
db.commit()

# ================= MENULAR =================

def lang_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O‘zbekcha")],
            [KeyboardButton(text="🇷🇺 Русский")],
            [KeyboardButton(text="🇬🇧 English")]
        ],
        resize_keyboard=True
    )

def main_menu(lang):
    texts = {
        "uz": ["⭐ Telegram Premium", "✨ Telegram Stars", "📢 Kanallarimiz", "✉️ Adminga xabar"],
        "ru": ["⭐ Telegram Premium", "✨ Telegram Stars", "📢 Наши каналы", "✉️ Написать админу"],
        "en": ["⭐ Telegram Premium", "✨ Telegram Stars", "📢 Our channels", "✉️ Message admin"],
    }
    t = texts[lang]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t[0]), KeyboardButton(text=t[1])],
                  [KeyboardButton(text=t[2]), KeyboardButton(text=t[3])]],
        resize_keyboard=True
    )

def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Reklama yuborish")],
            [KeyboardButton(text="👥 Foydalanuvchilar soni")]
        ],
        resize_keyboard=True
    )

# ================= UTILS =================

def get_user(user_id):
    cursor.execute("SELECT lang, last_msg FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def save_user(user_id, username, lang):
    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, username, lang, last_msg) VALUES (?,?,?,?)",
        (user_id, username, lang, 0)
    )
    db.commit()

async def check_subscription(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        )
    except:
        return False

def anti_spam(user_id):
    row = get_user(user_id)
    now = time.time()
    if row and row[1] and now - row[1] < ANTI_SPAM_SECONDS:
        return False
    cursor.execute("UPDATE users SET last_msg=? WHERE user_id=?", (now, user_id))
    db.commit()
    return True

# ================= BOT =================

async def main():
    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # START
    @dp.message(CommandStart())
    async def start(message: Message):
        save_user(message.from_user.id, message.from_user.username, "uz")
        await message.answer(
            "Tilni tanlang / Choose language / Выберите язык",
            reply_markup=lang_menu()
        )

    # LANGUAGE
    @dp.message(F.text.in_(["🇺🇿 O‘zbekcha", "🇷🇺 Русский", "🇬🇧 English"]))
    async def set_lang(message: Message):
        lang = "uz" if "O‘zbek" in message.text else "ru" if "Рус" in message.text else "en"
        save_user(message.from_user.id, message.from_user.username, lang)

        if not await check_subscription(bot, message.from_user.id):
            await message.answer(
                f"❗ Avval kanalga obuna bo‘ling:\nhttps://t.me/{CHANNEL_USERNAME.replace('@','')}"
            )
            return

        await message.answer("✅ OK", reply_markup=main_menu(lang))

    # PREMIUM
    @dp.message(F.text.contains("Premium"))
    async def premium(message: Message):
        if not anti_spam(message.from_user.id):
            return
        await message.answer(
            f"⭐ <b>Telegram Premium</b>\n\nSotib olish 👉 @{ADMIN_USERNAME}"
        )

    # STARS
    @dp.message(F.text.contains("Stars"))
    async def stars(message: Message):
        if not anti_spam(message.from_user.id):
            return
        await message.answer(
            "✨ <b>Telegram Stars</b>\n\n100 ⭐ = 28990 so'm \n500 ⭐ = 124990 so'm \n1000 ⭐ = 249990 so'm\n\n"
            f"Sotib olish 👉 @{ADMIN_USERNAME}"
        )

    # CHANNELS
    @dp.message(F.text.contains("Kanallar") | F.text.contains("канал") | F.text.contains("channels"))
    async def channels(message: Message):
        await message.answer(
            "📢 https://t.me/the7dvn\n📢 https://t.me/+8wSiiKO_kYY1NGY6"
        )

    # USER -> ADMIN MESSAGE
    @dp.message(F.text.contains("xabar") | F.text.contains("Message") | F.text.contains("Написать"))
    async def ask_message(message: Message):
        await message.answer("✉️ Xabaringizni yozing:")

    @dp.message()
    async def forward(message: Message):
        if message.from_user.id == ADMIN_ID:
            return
        if not anti_spam(message.from_user.id):
            return

        user = message.from_user
        await bot.send_message(
            ADMIN_ID,
            f"📩 <b>Yangi xabar</b>\n"
            f"👤 @{user.username}\n"
            f"🆔 <code>{user.id}</code>\n\n"
            f"{message.text}"
        )
        await message.answer("✅ Yuborildi")

    # ================= ADMIN =================

    @dp.message(CommandStart(), F.from_user.id == ADMIN_ID)
    async def admin_start(message: Message):
        await message.answer("👑 Admin panel", reply_markup=admin_menu())

    @dp.message(F.text == "👥 Foydalanuvchilar soni", F.from_user.id == ADMIN_ID)
    async def count(message: Message):
        cursor.execute("SELECT COUNT(*) FROM users")
        await message.answer(f"👥 Jami foydalanuvchilar: {cursor.fetchone()[0]}")

    @dp.message(F.text == "📢 Reklama yuborish", F.from_user.id == ADMIN_ID)
    async def broadcast_start(message: Message):
        await message.answer("📢 Yubormoqchi bo‘lgan xabarni yozing:")
        dp["broadcast"] = True

    @dp.message(F.from_user.id == ADMIN_ID)
    async def broadcast(message: Message):
        if not dp.get("broadcast"):
            return
        dp["broadcast"] = False

        cursor.execute("SELECT user_id FROM users")
        sent = 0
        for (uid,) in cursor.fetchall():
            try:
                await bot.send_message(uid, message.text)
                sent += 1
            except:
                pass
        await message.answer(f"✅ Yuborildi: {sent}")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
