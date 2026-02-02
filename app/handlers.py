from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    kb = [
        [KeyboardButton(text="/list")],
        [KeyboardButton(text="/add")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb,resize_keyboard=True)
    await message.answer("Я заставлю тебя работать маленькая сучка!", reply_markup=keyboard)


# Добавить в конец handlers.py
@router.message(F.photo | F.video | F.voice)
async def get_file_id_handler(message: Message):
    if message.photo:
        file_id = message.photo[-1].file_id
        await message.answer(f"ID фото: `{file_id}`", parse_mode="Markdown")
    elif message.video:
        await message.answer(f"ID видео: `{message.video.file_id}`", parse_mode="Markdown")
    elif message.voice:
        await message.answer(f"ID голосового: `{message.voice.file_id}`", parse_mode="Markdown")