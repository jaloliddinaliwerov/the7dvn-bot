from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = "8258746697:AAFOA2SI09YV_SMuIeq9lSmFN67k1fbeItk"
ADMIN_ID = 6734269605  # 👈 O'Z TELEGRAM ID INGIZNI QO'YING

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# 🔗 LINKLI TUGMALAR
BUTTON_1_TEXT = "Premium"
BUTTON_1_LINK = "https://t.me/m/zCrdNfrZMjJi"

BUTTON_2_TEXT = "Stars"
BUTTON_2_LINK = "https://t.me/m/f-d_Aqc1OGQ6"

# 📢 KANALLARINGIZ
CHANNELS_TEXT = (
    "📢 Xamkor kanallar:\n\n"
    "🔹 https://t.me/the7dvn\n"
    "🔹 Hamkorlikda ishlash uchun adminga murojaat qiling\n"
)

# 🧠 FSM
class AdminMessage(StatesGroup):
    waiting_for_message = State()


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(BUTTON_1_TEXT, url=BUTTON_1_LINK),
        types.InlineKeyboardButton(BUTTON_2_TEXT, url=BUTTON_2_LINK),
        types.InlineKeyboardButton("📢 Kanallarim", callback_data="channels"),
        types.InlineKeyboardButton("✉️ Adminga xabar", callback_data="admin_msg"),
    )

    await message.answer(
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=keyboard
    )


@dp.callback_query_handler(lambda c: c.data == "channels")
async def channels_handler(call: types.CallbackQuery):
    await call.message.answer(CHANNELS_TEXT)
    await call.answer()


@dp.callback_query_handler(lambda c: c.data == "admin_msg")
async def admin_msg_start(call: types.CallbackQuery):
    await call.message.answer("✍️ Xabaringizni yozing, men adminga yuboraman:")
    await AdminMessage.waiting_for_message.set()
    await call.answer()


@dp.message_handler(state=AdminMessage.waiting_for_message)
async def send_to_admin(message: types.Message, state: FSMContext):
    user = message.from_user

    text = (
        "📩 Yangi xabar:\n\n"
        f"👤 Ism: {user.full_name}\n"
        f"🔗 Username: @{user.username if user.username else 'yo‘q'}\n"
        f"🆔 ID: {user.id}\n\n"
        f"💬 Xabar:\n{message.text}"
    )

    await bot.send_message(ADMIN_ID, text)
    await message.answer("✅ Xabaringiz adminga yuborildi.")
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
