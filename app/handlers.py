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