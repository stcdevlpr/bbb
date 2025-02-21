from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Message, CallbackQuery, \
    KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

import data.user_data as db


router = Router()

def settings_menu_message(user_id):
    language = db.get_user_language(user_id)
    if language == "en":
        return (f"Select an option:")
    else:
        return (f"Выберите опцию:")


def create_settings_menu_keyboard(user_id):
    language = db.get_user_language(user_id)
    kb_builder = ReplyKeyboardBuilder()
    if language == "en":
        kb_builder.add(KeyboardButton(text="Language 🌍"))
        kb_builder.add(KeyboardButton(text="Support 🔧"))
        kb_builder.add(KeyboardButton(text="« Back"))
    else:
        kb_builder.add(KeyboardButton(text="Язык 🌍"))
        kb_builder.add(KeyboardButton(text="Поддержка 🔧"))
        kb_builder.add(KeyboardButton(text="« Назад"))
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


@router.message(F.text.regexp(r"(?i)настройки"))
@router.message(F.text.regexp(r"(?i)settings"))
async def settings_menu(message: Message):
    user_id = message.from_user.id
    text = settings_menu_message(user_id)
    await message.answer(text, reply_markup=create_settings_menu_keyboard(user_id))


def create_language_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="English 🇺🇸", callback_data="set_lang:en")
    builder.button(text="Русский 🇷🇺", callback_data="set_lang:ru")
    builder.adjust(1)
    return builder.as_markup()

# Создание инлайн-клавиатуры для выбора языка
def create_language_keyboard2():
    languages = [
        ("English", "en"),
        ("Русский", "ru"),
    ]
    buttons = [[InlineKeyboardButton(text=label, callback_data=f"set_lang:{code}") for label, code in languages]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@router.message(F.text.regexp(r"(?i)language"))
@router.message(F.text.regexp(r"(?i)язык"))
async def set_language_command(message: Message):
    user_id = message.from_user.id
    language = db.get_user_language(user_id)
    if language == "en":
        await message.answer("Please select a language:", reply_markup=create_language_keyboard())
    else:
        await message.answer("Пожалуйста, выберите язык:", reply_markup=create_language_keyboard())



@router.callback_query(F.data.startswith("set_lang"))
async def process_language_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    language_code = callback.data.split(":")[1]  # Получаем код языка из текста

    db.set_user_language(user_id, language_code)
    language = db.get_user_language(user_id)

    if language == "en":
        await callback.message.answer(
            f"Your language has been changed to ({language_code}) 🇺🇸.",
            reply_markup=create_settings_menu_keyboard(user_id)
        )
        await callback.message.delete()
    else:
        await callback.message.answer(
            f"Ваш язык был изменен на ({language_code}).",
            reply_markup=create_settings_menu_keyboard(user_id)
        )
        await callback.message.delete()


def support_menu_message(user_id):
    language = db.get_user_language(user_id)
    if language == "en":
        return (
            f"<b>Support 🔧</b>"
            f"\n\n"
            f"Our specialists are ready to answer any of your questions and help resolve any issues. Please contact us through the bot @DuskAirdropSupport, and we will get back to you as soon as possible!"
            f"\n\n"
            f"Support for the bot is available from 6:00 AM to 11:00 PM UTC."
            f"\n\n"
            f"🙏🏻 Please keep this in mind when reaching out."
        )
    else:
        return (
            f"<b>Поддержка 🔧</b>"
            f"\n\n"
            f"Наши специалисты готовы ответить на любые ваши вопросы и помочь в решении возникших проблем, напишите нам через бота @DuskAirdropSupport, и мы ответим вам в ближайшее время!"
            f"\n\n"
            f"Поддержка бота доступна с 6:00 до 23:00 по UTC."
            f"\n\n"
            f"🙏🏻 Пожалуйста, учитывайте это при обращении."
        )

@router.message(F.text.regexp(r"(?i)поддержка"))
@router.message(F.text.regexp(r"(?i)support"))
async def support_menu(message: Message):
    user_id = message.from_user.id
    text = support_menu_message(user_id)
    await message.answer(text, reply_markup=create_settings_menu_keyboard(user_id))