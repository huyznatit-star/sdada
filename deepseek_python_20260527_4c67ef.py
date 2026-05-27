from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import Database

def register_admin_handlers(dp: Dispatcher, db: Database, admin_id: int):
    @dp.message(Command("admin"))
    async def admin_panel(message: types.Message):
        if message.from_user.id != admin_id:
            await message.answer("Доступ запрещён.")
            return

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Редактировать Чекеры", callback_data="edit_checkers")],
            [InlineKeyboardButton(text="📝 Редактировать Парсеры", callback_data="edit_parsers")],
            [InlineKeyboardButton(text="📝 Редактировать Фермы", callback_data="edit_farms")],
            [InlineKeyboardButton(text="📝 Редактировать Автоматизацию", callback_data="edit_auto")],
            [InlineKeyboardButton(text="📝 Редактировать Цены", callback_data="edit_price")],
            [InlineKeyboardButton(text="📝 Редактировать Контакты", callback_data="edit_contact")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        ])
        await message.answer("Админ-панель:", reply_markup=kb)

    @dp.callback_query(lambda c: c.data and c.data.startswith("edit_"))
    async def edit_section(call: types.CallbackQuery):
        if call.from_user.id != admin_id:
            await call.answer("Доступ запрещён.", show_alert=True)
            return

        section = call.data.replace("edit_", "")
        current_text = db.get_text(section)
        await call.message.answer(
            f"Текущий текст раздела <b>{section}</b>:\n\n{current_text}\n\n"
            "Отправьте новый текст (можно использовать HTML-теги).",
            parse_mode="HTML"
        )
        await db.set_awaiting_input(call.from_user.id, section)
        await call.answer()

    @dp.callback_query(lambda c: c.data == "admin_stats")
    async def admin_stats(call: types.CallbackQuery):
        if call.from_user.id != admin_id:
            await call.answer("Доступ запрещён.", show_alert=True)
            return

        stats = db.get_stats()
        await call.message.answer(stats)
        await call.answer()

    @dp.message()
    async def handle_text_input(message: types.Message):
        if message.from_user.id != admin_id:
            return

        awaiting = db.get_awaiting_input(message.from_user.id)
        if awaiting:
            section = awaiting
            db.update_text(section, message.text)
            db.clear_awaiting_input(message.from_user.id)
            await message.answer(f"Текст раздела <b>{section}</b> обновлён.", parse_mode="HTML")