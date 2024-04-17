from aiogram import Router, F, Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter, Command

from core.keyboards.inline import *
from core.database.Table import table_user
from core.message.text import get_text_start_mess
from core.settings import settings

router = Router()


class SupportQuestion(StatesGroup):
    SetQuestion = State()


@router.message(CommandStart(), StateFilter(None))
async def start_handler(message: Message):
    admin = False
    if message.from_user.id == settings.bots.admin_id:
        admin = True
    await message.answer(get_text_start_mess(), reply_markup=create_start_buttons(admin))
    new_user = {
        "user_id": message.from_user.id,
        "username":message.from_user.username
    }
    if not(await table_user.get(user_id = message.from_user.id)):
        await table_user.create(new_user)