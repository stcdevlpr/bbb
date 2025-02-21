from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Задания", callback_data="tasks")
    builder.button(text="Кошелёк", callback_data="wallet")
    builder.button(text="Рейтинг", callback_data="rating")
    builder.button(text="Пригласить друзей", callback_data="invite")
    builder.button(text="Обучение", callback_data="education")
    builder.button(text="Новости", callback_data="news")
    builder.adjust(1)
    return builder.as_markup()


def link_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Official Airdrop Channel", url="https://t.me/+BZrIjYqqJTxhNWRi")],
    ])