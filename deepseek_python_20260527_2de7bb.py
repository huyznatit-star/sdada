import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from admin import register_admin_handlers

logging.basicConfig(level=logging.INFO)

API_TOKEN = "8590182019:AAFTy4TEhPLfoKK1hQYtU-i2xSQkieTvE1E"
ADMIN_ID = 8584601809

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
db = Database()

def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🛡️ Чекеры", callback_data="checkers"),
        InlineKeyboardButton(text="📊 Парсеры", callback_data="parsers"),
    )
    builder.row(
        InlineKeyboardButton(text="🎮 Фермы", callback_data="farms"),
        InlineKeyboardButton(text="🤖 Автоматизация", callback_data="auto"),
    )
    builder.row(
        InlineKeyboardButton(text="💰 Прайс-лист", callback_data="price"),
        InlineKeyboardButton(text="📞 Связаться", callback_data="contact"),
    )
    return builder.as_markup()

async def send_section(call: types.CallbackQuery, section: str):
    text = db.get_text(section)
    await call.message.edit_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
        ])
    )
    await db.log_click(call.from_user, section)
    await call.answer()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот-портфолио.\n"
        "Я сам — пример того, что мы умеем делать.\n\n"
        "Выбери категорию, чтобы увидеть примеры работ:",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(lambda c: c.data == "checkers")
async def show_checkers(call: types.CallbackQuery):
    await send_section(call, "checkers")

@dp.callback_query(lambda c: c.data == "parsers")
async def show_parsers(call: types.CallbackQuery):
    await send_section(call, "parsers")

@dp.callback_query(lambda c: c.data == "farms")
async def show_farms(call: types.CallbackQuery):
    await send_section(call, "farms")

@dp.callback_query(lambda c: c.data == "auto")
async def show_auto(call: types.CallbackQuery):
    await send_section(call, "auto")

@dp.callback_query(lambda c: c.data == "price")
async def show_price(call: types.CallbackQuery):
    await send_section(call, "price")

@dp.callback_query(lambda c: c.data == "contact")
async def show_contact(call: types.CallbackQuery):
    await send_section(call, "contact")

@dp.callback_query(lambda c: c.data == "back")
async def go_back(call: types.CallbackQuery):
    await call.message.edit_text(
        "👋 Привет! Я бот-портфолио.\n"
        "Я сам — пример того, что мы умеем делать.\n\n"
        "Выбери категорию, чтобы увидеть примеры работ:",
        reply_markup=get_main_keyboard()
    )
    await call.answer()

async def main():
    register_admin_handlers(dp, db, ADMIN_ID)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())