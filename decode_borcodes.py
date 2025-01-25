from importer_borcodes import *

decode_pylibdmtx = pylibdmtx.decode
decode_pyzbar = pyzbar.decode

class Form(StatesGroup):
    chooseform = State()
    create_code = State()

@form_router.message(Form.chooseform, F.text == "Декодинг и создание кодов")
async def process_scan_datam(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.create_code)
    folder_path = f"decode/{(message.from_user.id)}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    await message.reply(
        "Отправьте картинку с кодами или введите текст.\nПосле отправки необходимо подождать до 10 секунд и код создастся",
            reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отменить"),]],
            resize_keyboard=True,
        ),
    )

@form_router.message(Form.create_code)
async def process_create_qrcode(message: Message, state: FSMContext) -> None:
    await state.update_data(create_code=message)
    await message.answer('<i>Думаю</i>... ' + emoji.emojize(":thinking_face:"))
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=2,
    )
    if message.text:
        qr.add_data(message.text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"decode/{(message.from_user.id)}/result.jpg", "JPEG")
    if message.photo:
        file_name = f"decode/{(message.from_user.id)}/list.jpg" 
        await bot.download(message.photo[-1], destination=file_name)

        # image_gray = cv2.imread(f'decode/{(message.from_user.id)}/list.jpg', cv2.IMREAD_GRAYSCALE)
        # (thresh, image_bw) = cv2.threshold(image_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        # image_bw = cv2.threshold(image_gray, 127, 255, cv2.THRESH_BINARY)[1]
        # cv2.imwrite(f'decode/{(message.from_user.id)}/list.jpg', image_bw)

        img = cv2.imread(f"decode/{(message.from_user.id)}/list.jpg") 
        decodedList = decode_pylibdmtx(img)
        file_write = open(f"decode/{(message.from_user.id)}/list.txt", "w")
        for i in range(len(decodedList)):
            s = str(decodedList[i].data, "utf-8")
            file_write.write(s + '\n')
        file_write.close()
        file_read = open(f"decode/{(message.from_user.id)}/list.txt", "r")
        read = file_read.read()
        if read == '':
            decodedList_pyzbar = decode_pyzbar(img)
            f = open(f"decode/{(message.from_user.id)}/list.txt", "w")
            for i in range(len(decodedList_pyzbar)):
                s = str(decodedList_pyzbar[i].data, "utf-8")
                f.write(s + '\n')
            f.close()
            f2 = open(f"decode/{(message.from_user.id)}/list.txt", "r")
            read = f2.read()
            if read == '':
                print('do not have codes on picture')
                await message.answer('Я не смог найти штрихкоды на этом изображении ' + emoji.emojize(":pensive_face:") + '\nСможете скинуть изображение лучшего качества?\n\nЕсли Вы закончили, выберите Отменить')
                return
            qr.add_data(read[:-1])
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(f"decode/{(message.from_user.id)}/result.jpg", "JPEG")
            print('by pyzbar')
        else:
            qr.add_data(read[:-1])
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(f"decode/{(message.from_user.id)}/result.jpg", "JPEG")
            print('by pylibdmtx')

    await message.answer_photo(photo=FSInputFile(f"decode/{(message.from_user.id)}/result.jpg"),
        reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отменить"),]],
        resize_keyboard=True,
    ),)
    await message.answer(
        "Можете отправить еще изображение или ввести текст.\nЕсли Вы закончили, выберите Отменить",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отменить"),]],
            resize_keyboard=True,
        ),
    )