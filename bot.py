import asyncio
import logging
import sys
import pylibdmtx.pylibdmtx
import pyzbar.pyzbar
import qrcode
import cv2
import os
import token_1

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove)
from aiogram.types import FSInputFile
decode_pylibdmtx = pylibdmtx.pylibdmtx.decode
decode_pyzbar = pyzbar.pyzbar.decode
bot = Bot(token=token_1.token)
form_router = Router()



class Form(StatesGroup):
    chooseform = State()
    barcode_datam = State()
    barcode_other = State()

@form_router.message(CommandStart())
@form_router.message(F.text == "Старт")
async def process_name(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.chooseform)
    await message.answer(
        f"Привет, <b>{(message.from_user.first_name)}</b>!\nЯ могу создавать штрихкоды по введенному тексту и искать штрихкоды на приклепленной картинки и объединять все в один.\nВажно выбрать нужный тип кодов!",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Декодинг Матрикс-кодов"),
                    KeyboardButton(text="Декодинг остальных кодов"),
                ]
            ],
            resize_keyboard=True,
        ),
    )

@form_router.message(Command("Отменить"))
@form_router.message(F.text == "Отменить")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Действие отменено.\n\nнажми Старт, чтобы вернуться в главное меню!",
            reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Старт"),]],
            resize_keyboard=True,
                    )
    )

@form_router.message(Form.chooseform, F.text == "Декодинг Матрикс-кодов")
async def process_scan_datam(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.barcode_datam)
    folder_path = f"decode/{(message.from_user.id)}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    await message.reply(
        "Отправьте картинку с Матрикс-кодами или введи текст.\nПосле отправки подожди 2 секунды и код создастся",
            reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отменить"),]],
            resize_keyboard=True,
        ),
    )
@form_router.message(Form.chooseform, F.text == "Декодинг остальных кодов")
async def process_scan_datam(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.barcode_other)
    folder_path = f"decode/{(message.from_user.id)}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    await message.reply(
        "Отправьте картинку с кодами или введи текст.\nПосле отправки подожди 2 секунды и код создастся",
            reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отменить"),]],
            resize_keyboard=True,
        ),
    )

@form_router.message(Form.barcode_other)
async def process_create_qrcode(message: Message, state: FSMContext) -> None:
    await state.update_data(barcode_other=message)
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=2,
    )
    if message.photo:
        file_name = f"decode/{(message.from_user.id)}/list.jpg" 
        await bot.download(message.photo[-1], destination=file_name)
        img = cv2.imread(f"decode/{(message.from_user.id)}/list.jpg")
        decodedList_pyzbar = decode_pyzbar(img)
        f = open(f"decode/{(message.from_user.id)}/list.txt", "w")
        for i in range(len(decodedList_pyzbar)):
            s = str(decodedList_pyzbar[i].data, "utf-8")
            f.write(s + '\n')
        f.close()
        f2 = open(f"decode/{(message.from_user.id)}/list.txt", "r")
        read = f2.read()
        qr.add_data(read)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"decode/{(message.from_user.id)}/result.jpg", "JPEG")
    if message.text:
        qr.add_data(message.text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"decode/{(message.from_user.id)}/result.jpg", "JPEG")

    await message.answer_photo(photo=FSInputFile(f"decode/{(message.from_user.id)}/result.jpg"),
        reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отменить"),]],
        resize_keyboard=True,
    ),)
    await message.answer(
        "Можешь отправить еще фото или ввести текст.\nЕсли ты закончил, выбери Отменить",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отменить"),]],
            resize_keyboard=True,
        ),
    )

@form_router.message(Form.barcode_datam)
async def process_create_qrcode(message: Message, state: FSMContext) -> None:
    await state.update_data(barcode_datam=message)
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=2,
    )
    if message.photo:
        file_name = f"decode/{(message.from_user.id)}/list.jpg" 
        await bot.download(message.photo[-1], destination=file_name)
        img = cv2.imread(f"decode/{(message.from_user.id)}/list.jpg")
        decodedList = decode_pylibdmtx(img)
        f = open(f"decode/{(message.from_user.id)}/list.txt", "w")
        for i in range(len(decodedList)):
            s = str(decodedList[i].data, "utf-8")
            f.write(s + '\n')
        f.close()
        f2 = open(f"decode/{(message.from_user.id)}/list.txt", "r")
        read = f2.read()
        qr.add_data(read)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"decode/{(message.from_user.id)}/result.jpg", "JPEG")
    if message.text:
        qr.add_data(message.text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"decode/{(message.from_user.id)}/result.jpg", "JPEG")

    await message.answer_photo(photo=FSInputFile(f"decode/{(message.from_user.id)}/result.jpg"),
        reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отменить"),]],
        resize_keyboard=True,
    ),)
    await message.answer(
        "Можешь отправить еще фото или ввести текст.\nЕсли ты закончил, выбери Отменить",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отменить"),]],
            resize_keyboard=True,
        ),
    )


async def main():
    bot = Bot(token=token_1.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())