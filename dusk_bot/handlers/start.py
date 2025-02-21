from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram import flags

import data.user_data as db
import keyboards.inline as inl_kb
import keyboards.reply as rpl_kb
from data.сonfig import PHOTO_START_URL, REWARD_PER_INVITE, LOG_CHANNEL_ID

router = Router()

@router.message(Command("start"), F.chat.type == 'private', flags={"skip_logging": True})
async def start_handler(message: types.Message, bot: Bot):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="I totally agree ✅", callback_data="not_a_robot")
    )

    is_not_new_user = await db.user_exists(message.from_user.id)
    first_name = message.from_user.first_name
    user_id = message.from_user.id
    start_command = message.text
    invited_by = start_command[7:]

    if is_not_new_user:
        await bot.send_photo(
            message.from_user.id,
            photo=PHOTO_START_URL,
            caption=start_message(first_name, user_id),
            parse_mode="HTML",
            reply_markup=rpl_kb.user_menu(user_id)
        )

    else:
        if invited_by:
            if invited_by != str(message.from_user.id):
                try:
                    await db.add_user(message.from_user.id, int(invited_by))
                    await db.update_reward_status(message.from_user.id, 'not_received')

                    invited_by = await db.get_invited_by(message.from_user.id)
                    if invited_by:
                        message_inviter_id = (
                            f"⌛️ Your referral {first_name} has successfully registered and is under verification!"
                        )
                        await bot.send_message(invited_by, text=message_inviter_id, parse_mode="HTML")
                except Exception as e:
                    await message.answer(text=f"An error occurred: {e}.", show_alert=True)
            else:
                await bot.send_message(message.from_user.id, "Registering with your own referral link is prohibited!")
        else:
            try:
                await db.add_user(message.from_user.id, 0)
            except Exception as e:
                await message.answer(text=f"An error occurred: {e}", show_alert=True)

        info_text = (
            f"<b>New user registered!</b>\n\n"
            f"User ID: {user_id}\n"
            f"Profile Link: <a href='tg://user?id={user_id}'>{first_name}</a>.\n"
            f"Username: @{message.from_user.username}\n" if message.from_user.username else "No username\n"
            f"First Name: {first_name}\n"
            f"Last Name: {message.from_user.last_name}\n" if message.from_user.last_name else "No last name\n"
            f"Language Code: {message.from_user.language_code}\n" if message.from_user.language_code else "No language code\n"
        )
        await bot.send_message(LOG_CHANNEL_ID, info_text)

        message_text = (
            f"😮 <b>Wait a minute <a href='tg://user?id={user_id}'>{first_name}</a>!</b>"
            f"\n\n"
            f"Your $DUSK is waiting, but first you need to accept all terms of use policies to become a bot member! 👇"
        )
        await message.answer(message_text, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == 'not_a_robot', flags={"skip_logging": True})
async def handle_download_stats(callback_query: types.CallbackQuery, bot: Bot):
    await callback_query.answer(text="", show_alert=True)
    await callback_query.message.delete()

    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name

    try:
        await db.update_verification_status(user_id, is_verified=1)
        await callback_query.answer(f"Verification passed successfully, {first_name}! Good luck!")

        invited_by = await db.get_invited_by(user_id)
        if invited_by and invited_by != 0:
            reward_status = await db.get_reward_status(user_id)
            if reward_status == 'not_received':
                try:
                    await db.update_reward_status(user_id, 'received')
                    await bot.send_message(user_id, f"You have received +{REWARD_PER_INVITE} for registration via referral link!", parse_mode="HTML")
                    await bot.send_message(invited_by, f"You have received +{REWARD_PER_INVITE} for successfully inviting a user through the referral program!", parse_mode="HTML")

                    await db.update_user_balance(user_id, f"+{REWARD_PER_INVITE}")
                    await db.update_user_balance(invited_by, f"+{REWARD_PER_INVITE}")
                except Exception as e:
                    await callback_query.answer(text=f"An error occurred: {e}.", show_alert=True)

    except Exception as e:
        await callback_query.answer(text=f"Something went wrong: {e}.", show_alert=True)

    await bot.send_photo(
        callback_query.from_user.id,
        photo=PHOTO_START_URL,
        caption=start_message(first_name, user_id),
        reply_markup=rpl_kb.user_menu(user_id)
    )


def start_message(first_name: str, user_id: int) -> str:
    language = db.get_user_language(user_id)
    if language == "en":
        return (
            f"<b>👋 Hi <a href='{user_id}'>{first_name}</a>!</b> Get $DUSK for completing simple tasks and withdraw to your wallets!"
            f"\n\n"
            f"Dusk — is a proprietary token of the Dusk Network ecosystem, running on a Tier 1 blockchain, the Ethereum network under the ERC20 standard."
            f"\n\n"
            f'Dusk is already available for trading on leading exchanges: <a href="https://www.binance.com/en/trade/DUSK_USDT">Binance</a>, <a href="https://www.bitget.com/spot/DUSKUSDT">Bitget</a>, <a href="https://www.mexc.com/exchange/DUSK_USDT">MEXC</a> and many others!'
            f"\n\n"
            f"Subscribe to: <a href='https://t.me/+BZrIjYqqJTxhNWRi'>Official Airdrop Channel</a>"
        )
    else:
        return (
            f"<b> Привет, <a href='{user_id}'>{first_name}</a>!</b> Зарабатывай $DUSK, выполняя простые задания, и выводи их на свой кошелек!"
            f"\n\n"
            f"Dusk — это собственный токен экосистемы Dusk Network, работающий на блокчейне первого уровня, сети Ethereum по стандарту ERC-20."
            f"\n\n"
            f"Dusk уже торгуется на ведущих биржах: <a href='https://www.binance.com/en/trade/DUSK_USDT'>Binance</a>, <a href='https://www.bitget.com/spot/DUSKUSDT'>Bitget</a>, <a href='https://www.mexc.com/exchange/DUSK_USDT'>MEXC</a> и многих других!"
            f"\n\n"
            f"Подпишись на наш официальный канал Airdrop: <a href='https://t.me/+BZrIjYqqJTxhNWRi'>@DuskNetworkAirdrop</a>"
        )

@router.message(F.text.regexp(r"(?i)« back|« назад"))
async def set_language_command(message: Message, bot: Bot):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    await bot.send_photo(
        message.from_user.id,
        photo=PHOTO_START_URL,
        caption=start_message(first_name, user_id),
        parse_mode="HTML",
        reply_markup=rpl_kb.user_menu(user_id)
    )
