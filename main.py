import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.enums import ChatMemberStatus

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6734269605  # <-- O'Z ID
CHANNEL_ID = -1002057432941  # <-- MAJBURIY KANAL ID

# ===== LINKLAR =====
BOT_USERNAME = "https://t.me/by797_bot"
PREMIUM_BUY_LINK = "https://t.me/the_797"
STARS_BUY_LINK = "https://t.me/the_797"

# ===== NARXLAR =====
PREMIUM_TEXT = "⭐ Telegram Premium\n\n1 oy — 42 990 so‘m\n3 oy — 169 990 so‘m\n12 oy — 309 990 so‘m"
STARS_TEXT = "🌟 Telegram Stars\n\n100⭐ — 28 000 so‘m\n500⭐ — 124 990 so‘m\n1000⭐ — 249 990 so‘m"

# ===== SAQLASH =====
users = set()
referrals = {}        # user_id: count
discount_users = set()

# ===== KANAL TEKSHIRUV =====
async def check_subscription(bot, user_id):
    member = await bot.get_chat_member(CHANNEL_ID, user_id)
    return member.status in (
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    )

# ===== MENU =====
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 Xizmatlar")],
        [KeyboardButton(text="👥 Referal tizimi"), KeyboardButton(text="🎁 Chegirmam")],
        [KeyboardButton(text="📢 Kanallarim"), KeyboardButton(text="✉️ Adminga yozish")],
    ],
    resize_keyboard=True
)

services_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⭐ Telegram Premium", callback_data="premium")],
    [InlineKeyboardButton(text="🌟 Telegram Stars", callback_data="stars")],
])

def buy_kb(link, discount=False):
    text = "🛒 Sotib olish"
    if discount:
        text += " (-10%)"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, url=link)]
    ])

async def main():
    bot = Bot(TOKEN)
    dp = Dispatcher()

    # ===== START + REFERAL =====
    @dp.message(CommandStart())
    async def start(message: Message):
        args = message.text.split()
        user_id = message.from_user.id
        users.add(user_id)

        # Referal hisoblash
        if len(args) > 1:
            ref_id = int(args[1])
            if ref_id != user_id:
                referrals[ref_id] = referrals.get(ref_id, 0) + 1
                if referrals[ref_id] >= 10:
                    discount_users.add(ref_id)

        # Kanal tekshirish
        if not await check_subscription(bot, user_id):
            await message.answer(
                "❗ Botdan foydalanish uchun kanalga a’zo bo‘ling:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📢 Kanalga a’zo bo‘lish", url="https://t.me/the7dvn")],
                    [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]
                ])
            )
            return

        await message.answer(
            "👋 Xush kelibsiz!\nPastdagi menyudan foydalaning 👇",
            reply_markup=menu
        )

    @dp.callback_query(F.data == "check_sub")
    async def check_sub(call: CallbackQuery):
        if await check_subscription(bot, call.from_user.id):
            await call.message.answer("✅ Rahmat! Endi foydalanishingiz mumkin.", reply_markup=menu)
        else:
            await call.answer("❌ Hali kanalga a’zo emassiz", show_alert=True)

    # ===== XIZMATLAR =====
    @dp.message(F.text == "🛒 Xizmatlar")
    async def services(message: Message):
        await message.answer("Xizmatni tanlang:", reply_markup=services_kb)

    @dp.callback_query(F.data == "premium")
    async def premium(call: CallbackQuery):
        discount = call.from_user.id in discount_users
        text = PREMIUM_TEXT
        if discount:
            text += "\n\n🎁 Sizda 10% chegirma mavjud!"
        await call.message.answer(text, reply_markup=buy_kb(PREMIUM_BUY_LINK, discount))
        await call.answer()

    @dp.callback_query(F.data == "stars")
    async def stars(call: CallbackQuery):
        discount = call.from_user.id in discount_users
        text = STARS_TEXT
        if discount:
            text += "\n\n🎁 Sizda 10% chegirma mavjud!"
        await call.message.answer(text, reply_markup=buy_kb(STARS_BUY_LINK, discount))
        await call.answer()

    # ===== REFERAL =====
    @dp.message(F.text == "👥 Referal tizimi")
    async def ref_info(message: Message):
        uid = message.from_user.id
        count = referrals.get(uid, 0)
        link = f"https://t.me/{BOT_USERNAME}?start={uid}"

        await message.answer(
            f"👥 Referal tizimi\n\n"
            f"Taklif qilganlar: {count}/10\n"
            f"10 ta bo‘lsa → 🎁 10% chegirma\n\n"
            f"🔗 Sizning referal linkingiz:\n{link}"
        )

    # ===== CHEGIRMA =====
    @dp.message(F.text == "🎁 Chegirmam")
    async def discount(message: Message):
        if message.from_user.id in discount_users:
            await message.answer("🎉 Sizda 10% chegirma AKTIV!")
        else:
            await message.answer("❌ Hozircha chegirma yo‘q.\n10 ta do‘st taklif qiling.")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
