import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

# ===== SOZLAMALAR =====
TOKEN = os.getenv(8258746697:AAFOA2SI09YV_SMuIeq9lSmFN67k1fbeItk)  # Render env
ADMIN_ID = 6734269605  # <-- O'ZINGIZNI TELEGRAM ID QOYING

PREMIUM_CHAT_LINK = "https://t.me/m/zCrdNfrZMjJi"
STARS_CHAT_LINK = "https://t.me/m/f-d_Aqc1OGQ6"

CHANNELS_TEXT = (
    "📢 Hamkor kanallarim:\n\n"
    "🔹 https://t.me/the7dvn/n"
    "🔹 Hamkorlikda ishlash uchun adminga murojaat qiling\n"
)

# ===== TUGMALAR =====
def main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐ Telegram Premium", url=PREMIUM_CHAT_LINK),
            ],
            [
                InlineKeyboardButton(text="🌟 Telegram Stars", url=STARS_CHAT_LINK),
            ],
            [
                InlineKeyboardButton(text="📢 Kanallarim", callback_data="channels"),
            ],
            [
                InlineKeyboardButton(text="✉️ Adminga yozish", callback_data="admin"),
            ],
        ]
    )


async def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi")

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # ===== /start =====
    @dp.message(CommandStart())
    async def start_handler(message: Message):
        await message.answer(
            "👋 Salom!\n\n"
            "Bu bot orqali mening xizmatlarim bilan tanishishingiz mumkin.\n"
            "Quyidagi tugmalardan foydalaning ⬇️",
            reply_markup=main_keyboard(),
        )

    # ===== KANALLAR =====
    @dp.callback_query(F.data == "channels")
    async def channels_handler(call: CallbackQuery):
        await call.message.answer(CHANNELS_TEXT)
        await call.answer()

    # ===== ADMIN YOZISH BOSHLASH =====
    @dp.callback_query(F.data == "admin")
    async def admin_start(call: CallbackQuery):
        await call.message.answer(
            "✍️ Adminga yubormoqchi bo‘lgan xabaringizni yozing.\n\n"
            "Bekor qilish uchun /start bosing."
        )
        await call.answer()

    # ===== ADMIN GA XABAR YUBORISH =====
    @dp.message(F.text)
    async def forward_to_admin(message: Message):
        if message.from_user.id == ADMIN_ID:
            return

        text = (
            "📩 Yangi xabar:\n\n"
            f"👤 Foydalanuvchi: @{message.from_user.username}\n"
            f"🆔 ID: {message.from_user.id}\n\n"
            f"💬 Xabar:\n{message.text}"
        )

        await bot.send_message(ADMIN_ID, text)
        await message.answer("✅ Xabaringiz adminga yuborildi.")

    # ===== BOTNI ISHGA TUSHIRISH =====
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
