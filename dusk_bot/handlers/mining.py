import random
from datetime import timedelta, datetime

from aiogram import F, Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

import data.user_data as db

EMOJIS = ["💎", "🌀", "🌀"]
ENERGY_COST = 10
users_data = {}

router = Router()


@router.message(F.text.regexp(r"(?i)mining|майнинг"))
async def start_game(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_data:
        users_data[user_id] = {"coins": 0, "energy": 100}

    language = db.get_user_language(user_id)
    if language == "en":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="How does it work?", callback_data="how_it_works")],
            [InlineKeyboardButton(text="Start mining ⛏", callback_data="start_mining")]
        ])
        message_text = "Choose an action:"
        await message.answer(message_text, reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Как это работает?", callback_data="how_it_works")],
            [InlineKeyboardButton(text="Начать майнинг ⛏", callback_data="start_mining")]
        ])
        message_text = "Выберите действие:"
        await message.answer(message_text, reply_markup=keyboard)

def generate_keyboard():
    correct_index = random.randint(0, 2)
    builder = InlineKeyboardBuilder()
    for i in range(3):
        if i == correct_index:
            emoji = "💎"
        else:
            emoji = random.choice([e for e in EMOJIS if e != "💎"])
        builder.button(text=emoji, callback_data=f"pick:{i}:{correct_index}")
    builder.adjust(3)
    return builder.as_markup()


@router.callback_query(F.data.startswith("pick"))
async def handle_pick(query: types.CallbackQuery):
    user_id = query.from_user.id
    choice, correct_index = map(int, query.data.split(":")[1:])

    if user_id not in users_data:
        users_data[user_id] = {"coins": 0, "energy": 100}

    language = db.get_user_language(user_id)

    if choice == correct_index:
        if users_data[user_id]["energy"] >= ENERGY_COST:
            users_data[user_id]["coins"] += 0.50
            users_data[user_id]["energy"] -= ENERGY_COST
            if language == "en":
                message_text = f"<b>Congratulations!</b> You found a 💎 and earned 0.50 coins. Total coins: {users_data[user_id]['coins']}. Energy: {users_data[user_id]['energy']}"
                await db.update_user_balance(user_id,  f"+0.50")
            else:
                message_text = f"<b>Поздравляю!</b> Ты нашел 💎 и заработал 0.50 монет. Всего монет: {users_data[user_id]['coins']}. Энергия: {users_data[user_id]['energy']}"
                await db.update_user_balance(user_id, f"+0.50")
            await query.message.edit_text(message_text)
        else:
            if language == "en":
                message_text = "Not enough energy to mine. Wait or buy more energy."
            else:
                message_text = "Недостаточно энергии для добычи. Подожди или купи больше энергии."
            await query.message.edit_text(message_text)
    else:
        if language == "en":
            message_text = "You didn't find a 💎. Try again."
        else:
            message_text = "Ты не нашел 💎. Попробуй снова."
        await query.message.edit_text(message_text)


@router.callback_query(F.data == "how_it_works")
async def show_how_it_works(query: types.CallbackQuery):
    user_id = query.from_user.id
    language = db.get_user_language(user_id)
    if language == "en":
        message_text = "In this game, you need to choose the correct emoji to mine a 💎. Among the three emojis, only one is a 💎. If you choose the 💎, you will get an increase in your coin balance. Good luck!"
    else:
        message_text = "В этой игре вам нужно выбрать правильный эмодзи, чтобы добыть 💎. Среди трех эмодзи только один — это 💎. Если вы выберете 💎, вы получите прибавку к вашему балансу монет. Удачи!"
    await query.message.edit_text(message_text)


last_mining = {}

@router.callback_query(F.data == "start_mining")
async def start_mining(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    current_time = datetime.now()
    if user_id in last_mining:
        last_time = last_mining[user_id]
        if current_time - last_time < timedelta(minutes=30):
            # Пользователь обновляет информацию слишком часто
            user_language = db.get_user_language(user_id)
            if user_language == "en":
                await callback.answer("Mining dask is available every half an hour, check back later!",
                                      show_alert=True)
            else:
                await callback.answer(
                    "Добыча даска доступна каждые полчаса, загляните позже!",
                    show_alert=True)
            return

    # Обновляем временную метку последнего обновления
    last_mining[user_id] = current_time

    if user_id not in users_data:
        users_data[user_id] = {"coins": 0, "energy": 100}

    language = db.get_user_language(user_id)
    if language == "en":
        message_text = "Choose the correct emoji to mine a 💎:"
    else:
        message_text = "Выберите правильный эмодзи, чтобы добыть 💎:"

    await callback.message.edit_text(message_text, reply_markup=generate_keyboard())
