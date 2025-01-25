from importer_borcodes import *


help_buttons = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Какие штрихкоды я поддерживаю?', callback_data='help_1')],
                [InlineKeyboardButton(text='Как правильно отправлять фото?', callback_data='help_2')],
                ])


@form_router.message(F.text == "Помощь")
async def menu3(message: Message):
    await message.answer(
        'Навигация в помощи',
        reply_markup=help_buttons,
    )
@form_router.callback_query(F.data == 'help_1')
async def firstcallback(callback: CallbackQuery):
    text_help1 = 'Какие штрихкоды я поддерживаю? Я умею читать почти ВСЕ виды штрихкодов, от code128 до DataMatrix. Но создаю только в формате QRcode. Он самый "читабельный" по современным меркам.'
    input_help1 = InputMediaPhoto(media=FSInputFile('decode/help_codes.png'), caption=text_help1)
    await callback.message.edit_media(input_help1, reply_markup=callback.message.reply_markup)

@form_router.callback_query(F.data == 'help_2')
async def firstcallback(callback: CallbackQuery):
    text_help2 = 'Как правильно отправлять фото с массивом штрихкодов? Важно то, чтобы на отправленном фото были только те штрихкоды, которые должны быть отсканированы. На фото не должно быть других штрихкодов, которые являются частью других данных, иначе все "смешается".'
    input_help2 = InputMediaPhoto(media=FSInputFile('decode/goodcut.jpg'), caption=text_help2)
    await callback.message.edit_media(input_help2, reply_markup=callback.message.reply_markup)