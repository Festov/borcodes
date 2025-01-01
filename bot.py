import asyncio
import logging
import sys
import qrcode
import cv2
import re
import os
import token_1

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove)
from barcode import Code128
from barcode.writer import ImageWriter
from aiogram.types import FSInputFile
from pylibdmtx.pylibdmtx import decode 

bot = Bot(token=token_1.token)
form_router = Router()

class Form(StatesGroup):
    chooseform = State()
    createcode = State()
    scandatam = State()

@form_router.message(CommandStart())
@form_router.message(F.text == "Старт")
async def process_name(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.chooseform)
    await message.answer(
        f"Привет, <b>{(message.from_user.first_name)}</b>!\nЯ могу следующее:\n1. Создавать штрихкоды по введенному тексту\n2. Создавать QR код из массива Матрикс-кодов по фото.\n\nВыбери то, что хочешь использовать!",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Создать Штрихкод"),
                    KeyboardButton(text="Найти любовь"),
                    KeyboardButton(text="Создать QRcode"),
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

@form_router.message(Form.chooseform, F.text == "Создать QRcode")
async def process_scan_datam(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.scandatam)
    folder_path = f"decode/{(message.from_user.id)}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    await message.reply(
        "Отправьте картинку со списком кодов\nПосле отправки подожди 2 секунды и код создастся",
            reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отменить"),]],
            resize_keyboard=True,
        ),
    )

@form_router.message(Form.chooseform, F.text == "Создать Штрихкод")
async def process_create_barcode(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.createcode)
    await message.reply(
        "Хорошо, введи текст для штрихкода.\nВажно! Всё на английском!",
            reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отменить"),]],
            resize_keyboard=True,
        ),
    )
    

@form_router.message(Form.chooseform, F.text == "Найти любовь")
async def process_gvozdi(message: Message, state: FSMContext) -> None:
    await message.answer_photo(photo=FSInputFile('images/gvozdi.jpg'),
            reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отменить"),]],
            resize_keyboard=True,
        ),)

@form_router.message(Form.createcode)
async def process_create_code(message: Message, state: FSMContext) -> None:
    await state.update_data(createcode=message.text)
    bcode = message.text
    regex = "^[а-яА-ЯёЁ]+$"
    pattern = re.compile(regex)
    cyrillyc = pattern.search(bcode) is not None
    if cyrillyc is True:
        await message.answer(f"Русские буквы <b>НЕ</b> поддерживаются!\nТолько символы, цифры и английские буквы!")
        return process_create_barcode
    else:
        with open(f"barcodes/{(message.from_user.id)}.jpeg", "wb") as openfile:
            Code128(bcode, writer=ImageWriter()).write(openfile)
    await message.answer_photo(photo=FSInputFile(f'barcodes/{(message.from_user.id)}.jpeg'))
    openfile.close()
    await message.answer(
        "Если нужен еще ШК, то вводи текст.\nЕсли ты закончил, выбери Отменить",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отменить"),]],
            resize_keyboard=True,
        ),
    )

@form_router.message(Form.scandatam)
async def process_create_qrcode(message: Message, state: FSMContext) -> None:
    await state.update_data(scandatam=message.photo)
    if message.photo:
        file_name = f"decode/{(message.from_user.id)}/list.jpg" 
        await bot.download(message.photo[-1], destination=file_name)
    else:
        await message.answer('Нужно загрузить картинку!')
        return process_create_qrcode
    img = cv2.imread(f"decode/{(message.from_user.id)}/list.jpg")
    decodedList = decode(img)
    f = open(f"decode/{(message.from_user.id)}/list.txt", "w")
    for i in range(len(decodedList)):
        s = str(decodedList[i].data, "utf-8")
        f.write(s + '\n')
    f.close()
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
    )
    f2 = open(f"decode/{(message.from_user.id)}/list.txt", "r")
    read = f2.read()
    qr.add_data(read)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f"decode/{(message.from_user.id)}/result.jpg", "JPEG")
    await message.answer_photo(photo=FSInputFile(f"decode/{(message.from_user.id)}/result.jpg"),
        reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отменить"),]],
        resize_keyboard=True,
    ),)
    await message.answer(
        "Можешь отправить еще фото.\nЕсли ты закончил, выбери Отменить",
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