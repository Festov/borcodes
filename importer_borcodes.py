import asyncio
import logging
import sys
import qrcode
import cv2
import os
import token_1
import emoji

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery)
from aiogram.types import FSInputFile, input_media_photo, InputFile, InputMediaPhoto
from pylibdmtx import pylibdmtx
from pyzbar import pyzbar



bot = Bot(token=token_1.token)
form_router = Router()

@form_router.message(Command("Отменить"))
@form_router.message(F.text == "Отменить")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Действие отменено.",
            reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Меню"),]],
            resize_keyboard=True,
                    )
    )
    