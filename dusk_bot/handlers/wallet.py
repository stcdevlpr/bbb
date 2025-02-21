from datetime import timedelta, datetime

import aiohttp
from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import data.user_data as db

router = Router()


def get_wallet_message(user_id):
    language = db.get_user_language(user_id)
    if language == "en":
        return "Select an option:"
    else:
        return "Выберите опцию:"


async def get_dusk_info():
    url = "https://api.coingecko.com/api/v3/coins/dusk-network"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                # Предположим, что цена находится в поле "market_data" -> "current_price" -> "usd"
                return data['market_data']['current_price']['usd']
            else:
                return None



def create_wallet_keyboard(user_id):
    language = db.get_user_language(user_id)
    builder = InlineKeyboardBuilder()
    if language == "en":
        builder.button(text="Balance", callback_data="balance")
        builder.button(text="Transaction History", callback_data="transaction_history")
        builder.button(text="Withdraw", callback_data="withdraw")
    else:
        builder.button(text="Баланс", callback_data="balance")
        builder.button(text="История транзакций", callback_data="transaction_history")
        builder.button(text="Вывод средств", callback_data="withdraw")
    builder.adjust(1)
    return builder.as_markup()


@router.message(F.text.regexp(r"(?i)кошелёк|wallet"))
async def show_wallet(message: types.Message):
    user_id = message.from_user.id
    text = get_wallet_message(user_id)
    await message.answer(text, reply_markup=create_wallet_keyboard(user_id))


@router.callback_query(F.data == "back_wallet")
async def back_wallet(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text(get_wallet_message(user_id), reply_markup=create_wallet_keyboard(user_id))

last_update = {}

@router.callback_query(F.data == "balance")
async def balance(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        username = callback.from_user.username

        current_time = datetime.now()
        if user_id in last_update:
            last_time = last_update[user_id]
            if current_time - last_time < timedelta(minutes=1):
                # Пользователь обновляет информацию слишком часто
                user_language = db.get_user_language(user_id)
                if user_language == "en":
                    await callback.answer("Please wait before updating the balance again. (allowed once a minute)", show_alert=True)
                else:
                    await callback.answer("Пожалуйста, подождите перед повторным обновлением баланса. (разрешено раз в минуту)", show_alert=True)
                return

        # Обновляем временную метку последнего обновления
        last_update[user_id] = current_time

        price_info = await get_dusk_info()
        if price_info is None:
            user_language = db.get_user_language(user_id)
            if user_language == "en":
                await callback.answer("No pricing information could be obtained.", show_alert=True)
            else:
                await callback.answer("Не удалось получить информацию о цене.", show_alert=True)
            return

        balance = await db.get_user_balance(user_id)
        user_dusk_price = price_info * balance

        user_language = db.get_user_language(user_id)
        if user_language == "en":
            message_text = (
                f"<b>Balance:</b> {balance:.2f} DUSK$  <i>[{user_dusk_price:.2f} USD$]</i>"
            )
        else:
            message_text = (
                f"<b>Баланс:</b> {balance:.2f} DUSK$  <i>[{user_dusk_price:.2f} USD$]</i>"
            )

        message_text += f"\n<b>ID:</b> {user_id}"
        if username:
            message_text += f"\n<b>Username:</b> @{username}" if user_language == "en" else f"\n<b>Имя пользователя:</b> @{username}"

        await callback.message.edit_text(message_text, reply_markup=create_wallet_keyboard(user_id))

    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer("", show_alert=True)



@router.callback_query(F.data == "transaction_history")
async def transaction_history(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        message_text = (
            f"The transaction history does not contain any entries." if db.get_user_language(user_id) == "en" else
            f"История операций не содержит записей."
        )
        await callback.answer(message_text, show_alert=True)
        #await callback.message.edit_text(message_text, reply_markup=create_wallet_keyboard(user_id))
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer(f"", show_alert=True)


@router.callback_query(F.data == "withdraw")
async def withdraw(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        message_text = (
            f"We'll have to wait a little while!"
            f"\n\nThe withdrawal will be ready on September 19." if db.get_user_language(user_id) == "en" else
            f"Придется немного подождать!"
            f"\n\nВывод будет готов 19 сентября."
        )
        await callback.answer(message_text, show_alert=True)
        #await callback.message.edit_text(message_text, reply_markup=create_wallet_keyboard(user_id))

    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer(f"", show_alert=True)
