from aiogram import Router, types, F
import data.user_data as db

router = Router()

def format_rating_message(language, top_5_referrals, top_5_balances):
    if language == "en":
        referral_text = "\n".join([f"{i+1}. ID: {user_id} - Referrals: {count}"
                                   for i, (user_id, count) in enumerate(top_5_referrals)])
        balance_text = "\n".join([f"{i+1}. ID: {user_id} - Balance: {balance} DUSK$"
                                  for i, (user_id, balance) in enumerate(top_5_balances)])
        return (
            f"<b>🏆 User Rating:</b>\n\n"
            f"<b>Top 5 Referrals:</b>\n{referral_text}\n\n"
            f"<b>Top 5 Balances:</b>\n{balance_text}"
        )
    else:
        referral_text = "\n".join([f"{i+1}. ID пользователя: {user_id} - Рефералов: {count}"
                                   for i, (user_id, count) in enumerate(top_5_referrals)])
        balance_text = "\n".join([f"{i+1}. ID пользователя: {user_id} - Баланс: {balance} DUSK$"
                                  for i, (user_id, balance) in enumerate(top_5_balances)])
        return (
            f"<b>🏆 Рейтинг пользователей:</b>\n\n"
            f"<b>Топ-5 по рефералам:</b>\n{referral_text}\n\n"
            f"<b>Топ-5 по балансам:</b>\n{balance_text}"
        )

@router.message(F.text.regexp(r"(?i)рейтинг"))
@router.message(F.text.regexp(r"(?i)ranking"))
async def show_rating(message: types.Message):
    language = db.get_user_language(message.from_user.id)
    top_5_referrals, top_5_balances = db.get_top_5_referrals_and_balances()
    rating_message = format_rating_message(language, top_5_referrals, top_5_balances)
    await message.answer(rating_message)