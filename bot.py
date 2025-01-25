from importer_borcodes import *
from help_borcodes import *
from decode_borcodes import *


@form_router.message(CommandStart())
@form_router.message(F.text == "Старт")
@form_router.message(F.text == "Меню")
async def process_name(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.chooseform)
    await message.answer(
        f"Привет, <b>{(message.from_user.first_name)}</b>!\nЯ создаю штрихкоды типа QRcode. Могу генерировать штрихкод из текста и декодировать массив штрихкодов с картинки и объединять все в один штрихкод.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Декодинг и создание кодов"),
                    KeyboardButton(text='Помощь')
                ]
            ],
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