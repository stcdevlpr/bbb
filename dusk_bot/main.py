import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, BaseMiddleware, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.dispatcher.flags import get_flag
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update, User, Message
from aiogram.utils.formatting import Text
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.сonfig import API_TOKEN, LOG_CHANNEL_ID, ADMIN_USER_ID
from keyboards.reply import user_menu
from handlers import wallet, rating, start, settings, invite, mining, admin_panel
from aiogram import flags

from data import user_data as db


async def check_subscribe(user_id, bot: Bot):
    channels = db.get_active_channels()  # Получаем список каналов из базы данных

    for channel in channels:
        channel_name = channel[0]
        channel_id = channel[1]
        try:
            chat_member = await bot.get_chat_member(channel_id, user_id)
            if chat_member.status == 'left':
                keyboard = InlineKeyboardBuilder()

                # Добавляем кнопки с ссылками на все каналы
                for name, _, link in channels:
                    keyboard.add(types.InlineKeyboardButton(
                        text=name, url=link
                    ))

                keyboard.adjust(1)
                keyboard.add(types.InlineKeyboardButton(
                    text="Проверить", callback_data="check_subscription"
                ))

                await bot.send_message(
                    chat_id=user_id,
                    text="Вы должны подписаться на все каналы, чтобы использовать бота.",
                    reply_markup=keyboard.as_markup()
                )
                return False

        except Exception as e:
            await bot.send_message(LOG_CHANNEL_ID,  # Канал для логирования ошибок
                                   f"<b>Ошибка при проверке пользователя {user_id} на канале {channel_name} ({channel_id}):</b> {e}.")
            continue

    return True  # Пользователь подписан на все проверенные каналы


class SubscribeMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        user = event.from_user

        # Проверка на наличие флага skip_logging
        if get_flag(data, "skip_logging"):
            return await handler(event, data)

        bot = data['bot']
        is_subscribed = await check_subscribe(user.id, bot)

        if not is_subscribed:
            # Если пользователь не подписан на необходимые каналы
            return  # Прерываем выполнение, если проверка не пройдена

        # Логирование данных
        if user:
            logging_context = f"Handler: {handler.__name__}, User: {user.full_name} (ID: {user.id})"
            logging.info(logging_context)

        # Продолжаем выполнение хендлера
        return await handler(event, data)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher(storage=MemoryStorage())

router = Router()


@router.callback_query(F.data == "check_subscription", flags={"skip_logging": True})
async def check_subscription_handler(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id

    is_subscribed = await check_subscribe(user_id, bot)

    if is_subscribed:
        await callback_query.message.edit_text("Спасибо за подписку! Теперь вы можете пользоваться ботом.", reply_markup=user_menu(user_id))
    else:
        await callback_query.answer("Пожалуйста, подпишитесь на все каналы и попробуйте снова.", show_alert=True)
        await callback_query.message.delete()


router.include_router(wallet.router)
router.include_router(rating.router)
router.include_router(start.router)
router.include_router(settings.router)
router.include_router(mining.router)
router.include_router(invite.router)

router.include_router(admin_panel.router)

router.message.middleware(SubscribeMiddleware())
router.callback_query.middleware(SubscribeMiddleware())

dp.include_router(router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
