import asyncio
import os
import re

from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.сonfig import ADMIN_USER_ID
from data import user_data as db

from keyboards.reply import admin_menu

from data.сonfig import LOG_CHANNEL_ID, ADM_TID

router = Router()


@router.message(F.text == "!", flags={"skip_logging": True})
async def admin_command(message: types.Message):
    if message.from_user.id in ADMIN_USER_ID:
        message_text = (
            f"Успешная авторизация!"
        )
        await message.reply(message_text, reply_markup=admin_menu())


"""
===========================================================================
УПРАВЛЕНИЕ ОП
===========================================================================
"""


@router.message(F.text == "Управление ОП", flags={"skip_logging": True})
async def show_admin_commands(message: types.Message):
    if message.from_user.id in ADMIN_USER_ID:
        message_func = (
            "<b>Доступные команды:</b>\n\n"
            "<code>/add_channel</code> (channel_id) (name) (link)\n"
            "▪️ Добавляет новый канал в базу данных.\n\n"
            "<code>/toggle_channel</code> (channel_id) (status)\n"
            "▪️ Обновляет статус канала (on для активации и off для деактивации).\n\n"
            "<code>/remove_channel</code> name\n"
            "▪️ Удаляет все каналы с указанным именем из базы данных.\n\n"
            "<code>/list_channels</code>\n"
            "▪️ Показывает список всех каналов."
        )
        await message.answer(message_func)
    else:
        await message.reply('У вас нет доступа к этой команде.')


@router.message(Command("add_channel"), flags={"skip_logging": True})
async def add_channel_command(message: types.Message, bot: Bot):
    if message.from_user.id in ADMIN_USER_ID:
        try:
            # Регулярное выражение для извлечения аргументов, заключенных в скобки
            args = re.findall(r'\((.*?)\)', message.text)
            if len(args) != 3:
                await message.answer("Использование: /add_channel (channel_id) (name) (link)")
                return

            channel_id, name, link = args
            db.add_channel(name, channel_id, link)
            await message.answer(f"Канал {name} был успешно добавлен.")
            await bot.send_message(LOG_CHANNEL_ID,
                                   f"Канал {name} был успешно добавлен.",
                                   message_thread_id=ADM_TID)

        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")
    else:
        await message.reply('У вас нет доступа к этой команде.')


@router.message(Command("toggle_channel"), flags={"skip_logging": True})
async def toggle_channel_command(message: types.Message, bot: Bot):
    if message.from_user.id in ADMIN_USER_ID:
        try:
            args = message.text.split()
            if len(args) != 3:
                await message.answer("Использование: /toggle_channel <channel_id> <status>")
                return

            _, channel_id, status = args
            is_active = 1 if status.lower() == 'on' else 0
            db.update_channel_status(channel_id, is_active)
            await message.answer(
                f"Статус канала {channel_id} был обновлен на {'активен' if is_active else 'неактивен'}.")
            await bot.send_message(LOG_CHANNEL_ID,
                                   f"Статус канала {channel_id} был обновлен на {'активен' if is_active else 'неактивен'}.",
                                   message_thread_id=ADM_TID)

        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")
    else:
        await message.reply('У вас нет доступа к этой команде.')


@router.message(Command("remove_channel"), flags={"skip_logging": True})
async def remove_channel_command(message: types.Message, bot: Bot):
    if message.from_user.id in ADMIN_USER_ID:
        try:
            args = message.text.split(maxsplit=1)
            if len(args) != 2:
                await message.answer("Использование: /remove_channel <name>")
                return

            _, name = args
            db.remove_channel_by_name(name)
            await message.answer(f"Все каналы с именем {name} были успешно удалены.")
            await bot.send_message(LOG_CHANNEL_ID,
                                   f"Все каналы с именем {name} были успешно удалены.",
                                   message_thread_id=ADM_TID)
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")
    else:
        await message.reply('У вас нет доступа к этой команде.')


@router.message(Command("list_channels"), flags={"skip_logging": True})
async def list_channels_command(message: types.Message):
    if message.from_user.id in ADMIN_USER_ID:
        try:
            channels = db.get_all_channels()
            if not channels:
                await message.answer("Каналов не найдено.")
            else:
                message_text = "\n".join([
                    f"Имя: {channel[0]}"
                    f"\n"
                    f"ID: <code>{channel[1]}</code>"
                    f"\n"
                    f"Ссылка: {channel[2]}"
                    f"\n"
                    f"Статус: {'активен' if channel[3] == 1 else 'неактивен'}"
                    f"\n"
                    for channel in channels
                ])
                await message.answer(message_text, disable_web_page_preview=True)
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")
    else:
        await message.reply('У вас нет доступа к этой команде.')


"""
===========================================================================
БЛОКИРОВКА ПОЛЬЗОВАТЕЛЕЙ
===========================================================================
"""


@router.message(F.text == "Блокировать пользователя", flags={"skip_logging": True})
async def show_admin_commands(message: types.Message):
    if message.from_user.id in ADMIN_USER_ID:
        message_func = (
            "<b>Временно недоступно.</b>"
        )
        await message.answer(message_func)
    else:
        await message.reply('У вас нет доступа к этой команде.')


"""
===========================================================================
ПОЛУЧИТЬ СТАТИСТИКУ
===========================================================================
"""


@router.message(F.text == "Получить статистику", flags={"skip_logging": True})
async def show_statistics(message: types.Message):
    if message.from_user.id in ADMIN_USER_ID:
        try:
            total_users, active_users, inactive_users = db.get_subscription_statistics()
            message_func = (
                f"<b>Статистика подписчиков:</b>\n"
                f"Всего подписчиков: {total_users}\n"
                f"Активные: {active_users}\n"
                f"Неактивные: {inactive_users}"
            )
            await message.answer(message_func, parse_mode="HTML")
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")
    else:
        await message.reply('У вас нет доступа к этой команде.')


"""
===========================================================================
ОТПРАВИТЬ РАССЫЛКУ
===========================================================================
"""


# Состояния для FSM
class AdminStates(StatesGroup):
    waiting_for_broadcast_message = State()
    waiting_for_user_range = State()
    waiting_for_confirmation = State()
    waiting_for_image = State()
    waiting_for_button = State()

@router.message(F.text == "Отправить рассылку", flags={"skip_logging": True})
async def send_broadcast_prompt(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_USER_ID:
        await message.reply('Введите сообщение для рассылки:')
        await state.set_state(AdminStates.waiting_for_broadcast_message)


@router.message(AdminStates.waiting_for_broadcast_message, flags={"skip_logging": True})
async def handle_broadcast_message(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_USER_ID:
        await state.update_data(broadcast_message=message.html_text)

        total_users, active_users, inactive_users = db.get_subscription_statistics()

        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="Отменить ❌", callback_data="cancel")

        await message.reply(
            f"Введите диапазон пользователей для рассылки (активных: {active_users}, неактивных: {inactive_users}, всего: {total_users}):\nПример: 100-500",
            reply_markup=keyboard.as_markup()
        )
        await state.set_state(AdminStates.waiting_for_user_range)


@router.message(AdminStates.waiting_for_user_range, flags={"skip_logging": True})
async def handle_user_range_message(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_USER_ID:
        try:
            user_range = list(map(int, message.text.split('-')))
            if len(user_range) != 2 or user_range[0] > user_range[1] or any(n < 0 for n in user_range):
                raise ValueError("Неверный диапазон пользователей.")

            await state.update_data(user_from=user_range[0], user_to=user_range[1])
            data = await state.get_data()
            broadcast_message = data.get('broadcast_message')

            keyboard = InlineKeyboardBuilder()
            keyboard.row(
                InlineKeyboardButton(text="Подтвердить ✔️", callback_data="confirm"),
                InlineKeyboardButton(text="Отменить ❌", callback_data="cancel")
            )
            keyboard.row(
                InlineKeyboardButton(text="Добавить кнопку ➕", callback_data="add_button"),
                InlineKeyboardButton(text="Загрузить изображение 🖼", callback_data="upload_image")
            )

            await message.reply("Вы хотите отправить это сообщение?", reply_markup=keyboard.as_markup())
            await state.set_state(AdminStates.waiting_for_confirmation)
        except ValueError:
            await message.reply('Ошибка! Введите правильный диапазон пользователей.')


@router.message(AdminStates.waiting_for_image, F.photo, flags={"skip_logging": True})
async def handle_image_message(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_USER_ID:
        photo = message.photo[-1]
        await state.update_data(image=photo.file_id)

        data = await state.get_data()
        broadcast_message = data.get('broadcast_message')

        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(text="Подтвердить ✅", callback_data="confirm"),
            InlineKeyboardButton(text="Отменить ❌", callback_data="cancel")
        )
        keyboard.row(
            InlineKeyboardButton(text="Добавить кнопку ➕", callback_data="add_button"),
        )
        keyboard.row(
            InlineKeyboardButton(text="Удалить изображение ❌", callback_data="delete_image")
        )

        await message.reply_photo(photo.file_id, caption=broadcast_message, reply_markup=keyboard.as_markup())
        await state.set_state(AdminStates.waiting_for_confirmation)


@router.callback_query(F.data == 'upload_image', flags={"skip_logging": True})
async def process_upload_image(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, "Загрузите изображение:")
    await state.set_state(AdminStates.waiting_for_image)


@router.callback_query(F.data == 'delete_image', flags={"skip_logging": True})
async def process_delete_image(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(image=None)
    data = await state.get_data()
    broadcast_message = data.get('broadcast_message')

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="Подтвердить ✅", callback_data="confirm"),
        InlineKeyboardButton(text="Отменить ❌", callback_data="cancel")
    )
    keyboard.row(
        InlineKeyboardButton(text="Добавить кнопку ➕", callback_data="add_button"),
        InlineKeyboardButton(text="Загрузить изображение 🖼", callback_data="upload_image")
    )

    await bot.send_message(callback_query.from_user.id, broadcast_message, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == 'confirm', flags={"skip_logging": True})
async def process_confirm(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()
    data = await state.get_data()
    broadcast_message = data.get('broadcast_message')
    image = data.get('image')
    user_from = data.get('user_from')
    user_to = data.get('user_to')

    users = db.get_all_users()[user_from:user_to]
    total_users = len(users)

    message = await bot.send_message(callback_query.from_user.id, "Начинаем рассылку...")

    successful_count = 0
    failed_count = 0
    delivery_status = {}

    for idx, user in enumerate(users):
        try:
            if image:
                await bot.send_photo(user[0], image, caption=broadcast_message)
            else:
                await bot.send_message(user[0], broadcast_message)
            db.reset_failed_send(user[0])
            successful_count += 1
            delivery_status[user[0]] = "Delivered"
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user[0]}: {e}")
            db.increment_failed_send(user[0])
            failed_count += 1
            delivery_status[user[0]] = "Not delivered"

        if (idx + 1) % 1500 == 0:
            await asyncio.sleep(300)  # Перерыв 5 минут

        if total_users > 0 and (total_users >= 10 and idx % (total_users // 10) == 0):
            progress = (idx + 1) / total_users * 100
            await message.edit_text(
                f"Прогресс: {progress:.2f}%\n"
                f"Успешно: {successful_count}\n"
                f"Не удалось: {failed_count}\n"
                f"Текущий пользователь: {user[0]}"
            )

    await bot.send_message(callback_query.from_user.id,
                           f'<b>Общая статистика рассылки:</b>\n\nСообщение было успешно отправлено: {successful_count}\nНе удалось отправить сообщение: {failed_count}',
                           parse_mode="html")

    stats_filename = 'stats.txt'
    with open(stats_filename, 'w') as file:
        file.write(f'Successful: {successful_count}\n')
        file.write(f'Failed: {failed_count}\n')
        file.write('Sent to users:\n')
        for index, (user_id, status) in enumerate(delivery_status.items(), start=1):
            file.write(f'{index}. User ID: {user_id}, Status: {status}\n')

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Загрузить файл статистики 💾", callback_data="download_stats")

    await bot.send_message(callback_query.from_user.id,
                           '<b>Завершена рассылка, загрузить файл подробной статистики?</b>',
                           parse_mode="html", reply_markup=keyboard.as_markup())
    await state.clear()


@router.callback_query(F.data == 'cancel', flags={"skip_logging": True})
async def process_cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer(text="Успешно отменено!", show_alert=True)
    await state.clear()


@router.callback_query(F.data == 'add_button', flags={"skip_logging": True})
async def process_add_button(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id,
                           'Введите кнопки в формате "название - ссылка", каждая кнопка на новой строке:')
    await state.set_state(AdminStates.waiting_for_button)


@router.message(AdminStates.waiting_for_button, flags={"skip_logging": True})
async def handle_button_message(message: types.Message, state: FSMContext, bot: Bot):
    if message.from_user.id in ADMIN_USER_ID:
        try:
            data = await state.get_data()
            broadcast_message = data.get('broadcast_message')
            existing_keyboard = data.get('keyboard')
            image = data.get('image')

            buttons = []
            for line in message.text.strip().split('\n'):
                title, url = line.split(' - ', 1)
                buttons.append(InlineKeyboardButton(text=title, url=url))

            if existing_keyboard:
                existing_keyboard.inline_keyboard.append(buttons)
                keyboard = existing_keyboard
            else:
                keyboard = InlineKeyboardBuilder()
                keyboard.row(*buttons)

            await state.update_data(keyboard=keyboard.as_markup())

            if image:
                await bot.send_photo(message.from_user.id, image, caption=broadcast_message,
                                     reply_markup=keyboard.as_markup())
            else:
                await bot.send_message(message.from_user.id, broadcast_message, reply_markup=keyboard.as_markup())

            keyboard_confirmation = InlineKeyboardBuilder()
            keyboard_confirmation.row(
                InlineKeyboardButton(text="Подтвердить ✅", callback_data="confirm"),
                InlineKeyboardButton(text="Отменить ❌", callback_data="cancel")
            )
            keyboard_confirmation.button(text="Добавить кнопку ➕", callback_data="add_button")

            await bot.send_message(message.from_user.id, "Кнопки добавлены. Вы хотите отправить это сообщение?",
                                   reply_markup=keyboard_confirmation.as_markup())
            await state.set_state(AdminStates.waiting_for_confirmation)
        except ValueError:
            await bot.send_message(message.from_user.id,
                                   'Произошла ошибка при добавлении кнопок. Проверьте формат и попробуйте снова.')
    else:
        await message.reply('Произошла ошибка.')


@router.callback_query(F.data == 'download_stats', flags={"skip_logging": True})
async def handle_download_stats(callback_query: types.CallbackQuery, bot: Bot):
    stats_filename = 'stats.txt'
    await callback_query.answer()

    if os.path.isfile(stats_filename):
        await bot.send_document(callback_query.from_user.id, FSInputFile(stats_filename))
        os.remove(stats_filename)
    else:
        await callback_query.answer(text="❌ Документ не найден или уже был загружен!", show_alert=True)

"""
===========================================================================
ОБНУЛЕНИЕ ПОЛЬЗОВАТЕЛЯ
===========================================================================
"""


class DelStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_confirmation = State()


# Команда для инициации удаления пользователя
@router.message(F.text == "/delete_user", flags={"skip_logging": True})
async def ask_user_id_for_deletion(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_USER_ID:
        await message.answer("Введите ID пользователя, которого хотите удалить:")
        await state.set_state(DelStates.waiting_for_user_id)
    else:
        await message.reply("У вас нет доступа к этой команде.")


# Обработка введенного user_id
@router.message(DelStates.waiting_for_user_id)
async def confirm_user_deletion(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_USER_ID:
        user_id = message.text

        # Сохраняем user_id в данные состояния
        await state.update_data(user_id=user_id)

        # Создаем клавиатуру с кнопками подтверждения и отмены
        kb = InlineKeyboardBuilder()
        kb.button(text="Подтвердить удаление", callback_data="confirm_deletion")
        kb.button(text="Отменить", callback_data="cancel_deletion")
        await message.answer(f"Вы уверены, что хотите удалить пользователя с ID: {user_id}?",
                             reply_markup=kb.as_markup())

        await state.set_state(DelStates.waiting_for_confirmation)
    else:
        await message.reply("У вас нет доступа к этой команде.")


# Обработка подтверждения или отмены
@router.callback_query(F.data == "confirm_deletion")
async def delete_user_confirmed(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = data.get('user_id')

    if user_id:
        db.delete_user_data(int(user_id))  # Функция удаления данных пользователя из базы данных
        await bot.send_message(callback.from_user.id, f"Данные пользователя с ID: {user_id} были удалены.")
    else:
        await bot.send_message(callback.from_user.id, "Ошибка: не удалось найти ID пользователя.")

    await state.clear()


@router.callback_query(F.data == "cancel_deletion")
async def cancel_user_deletion(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(callback.from_user.id, "Удаление пользователя отменено.")
    await state.clear()