import sqlite3
import os
from typing import Optional
from typing import List, Tuple


DB_PATH = os.path.join('data', 'user.db')

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0,
            invited_by INTEGER,
            reward_status TEXT DEFAULT 'not_received',
            is_verified INTEGER DEFAULT 0,
            language TEXT DEFAULT 'en',
            FOREIGN KEY(invited_by) REFERENCES users(user_id)
        )
    """)
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS failed_sends (
                user_id INTEGER PRIMARY KEY,
                fail_count INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
                ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                channel_id TEXT,
                link TEXT,
                is_active INTEGER DEFAULT 1
            )
                ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS ban_list (
                user_id INTEGER,
                reason TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
              ''')
    conn.commit()
    conn.close()


async def user_exists(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


async def add_user(user_id: int, invited_by: Optional[int]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, invited_by) VALUES (?, ?)", (user_id, invited_by))
    conn.commit()
    conn.close()


async def update_reward_status(user_id: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET reward_status = ? WHERE user_id = ?", (status, user_id))
    conn.commit()
    conn.close()


async def get_invited_by(user_id: int) -> Optional[int]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT invited_by FROM users WHERE user_id = ?", (user_id,))
    referrer_id = cursor.fetchone()
    conn.close()
    return referrer_id[0] if referrer_id else None


async def update_user_balance(user_id: int, amount: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()


async def get_reward_status(user_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT reward_status FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'not_received'


async def update_verification_status(user_id: int, is_verified: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_verified = ? WHERE user_id = ?', (is_verified, user_id))
    conn.commit()
    conn.close()


async def is_user_verified(user_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT is_verified FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] == 1 if result else False


# Функция для установки языка пользователя
def set_user_language(user_id: int, language: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
    conn.commit()
    conn.close()


# Функция для получения языка пользователя
def get_user_language(user_id: int) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'en'  # Если язык не установлен, по умолчанию 'en'


async def get_user_balance(user_id: int) -> float:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0.0


async def get_invite_data(user_id: int) -> tuple:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM users 
        WHERE invited_by = ? AND is_verified = 1
    """, (user_id,))
    verified_invites = cursor.fetchone()[0]

    conn.close()
    return verified_invites


def get_top_5_referrals_and_balances():
    conn = get_connection()
    cursor = conn.cursor()

    # Топ-5 по количеству рефералов
    cursor.execute("""
        SELECT user_id, COUNT(*) AS referral_count
        FROM users
        WHERE is_verified = 1
        GROUP BY user_id
        ORDER BY referral_count DESC
        LIMIT 5
    """)
    top_5_referrals = cursor.fetchall()

    # Топ-5 по балансу
    cursor.execute("""
        SELECT user_id, balance
        FROM users
        ORDER BY balance DESC
        LIMIT 5
    """)
    top_5_balances = cursor.fetchall()

    conn.close()
    return top_5_referrals, top_5_balances


def get_active_channels2():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT name, channel_id, link FROM channels WHERE is_active = 1')
    channels = cursor.fetchall()

    conn.close()
    return channels


"""
===========================================================================
ADMIN PANNEL
===========================================================================
"""

# Добавление нового канала в базу данных
def add_channel(name: str, channel_id: str, link: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO channels (name, channel_id, link)
            VALUES (?, ?, ?)
        ''', (name, channel_id, link))
        conn.commit()

# Обновление статуса канала
def update_channel_status(channel_id: str, is_active: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE channels
            SET is_active = ?
            WHERE channel_id = ?
        ''', (is_active, channel_id))
        conn.commit()

# Удаление канала из базы данных по имени
def remove_channel_by_name(name: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM channels
            WHERE name = ?
        ''', (name,))
        conn.commit()

# Получение списка всех активных каналов
def get_active_channels() -> List[Tuple[str, str, str]]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, channel_id, link 
            FROM channels 
            WHERE is_active = 1
        ''')
        return cursor.fetchall()

# Получение списка всех каналов (активных и неактивных)
def get_all_channels() -> List[Tuple[str, str, str, int]]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, channel_id, link, is_active 
            FROM channels
        ''')
        return cursor.fetchall()

# Получение списка статистики подписчиков
def get_subscription_statistics() -> Tuple[int, int, int]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]

        cursor.execute('''
            SELECT COUNT(*)
            FROM users
            WHERE user_id IN (SELECT user_id FROM failed_sends WHERE fail_count > 1)
        ''')
        inactive_users = cursor.fetchone()[0]

        active_users = total_users - inactive_users

    finally:
        cursor.close()
        conn.close()

    return total_users, active_users, inactive_users


# Рассылка
def reset_failed_send(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM failed_sends WHERE user_id = ?', (user_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def increment_failed_send(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO failed_sends (user_id, fail_count)
            VALUES (?, 1)
            ON CONFLICT(user_id)
            DO UPDATE SET fail_count = fail_count + 1
        ''', (user_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT user_id FROM users')
        users = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return users


# Функция для удаления данных пользователя из базы данных
def delete_user_data(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM failed_sends WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM ban_list WHERE user_id = ?', (user_id,))
        conn.commit()
    except Exception as e:
        print(f"Произошла ошибка при удалении данных пользователя: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

initialize_database()