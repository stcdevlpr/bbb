import aiohttp
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

import random
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import data.user_data as db
from data.сonfig import BOT_USERNAME, REWARD_PER_INVITE

router = Router()

@router.message(F.text.regexp(r"(?i)пригласить друзей|invite friends"))
async def send_dusk_info(message: Message):
    user_id = message.from_user.id

    language = db.get_user_language(user_id)
    verified_invites = await db.get_invite_data(user_id)
    earned_reward = verified_invites * REWARD_PER_INVITE

    if language == "en":
        message_text = (
            f"👥 <b>Invite your friends and top up your DUSK balance for each person you invite!</b>"
            f"\n\n"
            f"You invited: {verified_invites} users"
            f"\n"
            f"Award Received: {earned_reward} DUSK$"
            f"\n\n"
            f"<b>Your inviting link:</b>"
            f"\n"
            f"<code>https://t.me/{BOT_USERNAME}?start={user_id}</code>"
            f"\n\n"
            f"<b>Terms and Requirements:</b>"
            f"\n"
            f"1) The invited user must successfully register in the bot using your link."
            f"\n"
            f"2) Next, confirm the project rules and go to the menu."
            f"\n"
            f"3) After you both will receive your reward."
            f"\n\n"
        )
        await message.answer(message_text)
    else:
        message_text = (
            f"👥 Приглашайте друзей и пополняйте свой баланс DUSK за каждого приглашенного!"
            f"\n\n" 
            f"Вы пригласили: {verified_invites} пользователей"
            f"\n"
            f"Полученное вознаграждение: {earned_reward} DUSK$"
            f"\n\n"
            f"<b>Ваша пригласительная ссылка:</b>"
            f"\n"
            f"<code>https://t.me/{BOT_USERNAME}?start={user_id}</code>"
            f"\n\n"
            f"<b>Условия и требования:</b>"
            f"\n"
            f"1) Приглашённый пользователь должен успешно зарегистрироваться в боте по вашей ссылке."
            f"\n"
            f"2) Затем подтвердите правила проекта и перейдите в меню."
            f"\n"
            f"3) После этого вы оба получите своё вознаграждение."
            f"\n\n"
        )
        await message.answer(message_text)