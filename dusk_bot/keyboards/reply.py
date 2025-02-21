from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import data.user_data as db


def user_menu(user_id):

    language = db.get_user_language(user_id)
    if language == "en":
        keyboard = [
            [types.KeyboardButton(text="Wallet 👛"), types.KeyboardButton(text="Mining ⛏")],
            [types.KeyboardButton(text="Ranking 🏆"), types.KeyboardButton(text="Invite Friends 👥")],
            [types.KeyboardButton(text="Settings ⚙️")]
        ]
    else:
        keyboard = [
            [types.KeyboardButton(text="Кошелёк 👛"), types.KeyboardButton(text="Майнинг ⛏")],
            [types.KeyboardButton(text="Рейтинг 🏆"), types.KeyboardButton(text="Пригласить друзей 👥")],
            [types.KeyboardButton(text="Настройки ⚙️")]
        ]

    return types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=keyboard
    )

def admin_menu():

    keyboard = [
        [types.KeyboardButton(text="Управление ОП"), types.KeyboardButton(text="Блокировать пользователя")],
        [types.KeyboardButton(text="Получить статистику"), types.KeyboardButton(text="Отправить рассылку")],
        [types.KeyboardButton(text="Управление балансами")]
    ]

    return types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=keyboard
    )
