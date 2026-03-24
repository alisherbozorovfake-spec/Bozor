import logging
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN, ADMIN_ID, CHANNEL_ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# DATABASE
db = sqlite3.connect("database.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
""")

db.commit()

# MENU
def main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📤 UC Sotish", "📥 UC Sotib olish")
    keyboard.add("💰 Hisob", "🆘 Yordam")
    return keyboard

# START
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    db.commit()
    await message.answer("Xush kelibsiz!", reply_markup=main_menu())

# 1️⃣ UC SOTISH
@dp.message_handler(lambda m: m.text == "📤 UC Sotish")
async def sell_uc(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("60 UC", "120 UC", "240 UC")
    kb.add("325 UC", "385 UC", "660 UC")
    await message.answer("UC tanlang:", reply_markup=kb)

@dp.message_handler(lambda m: "UC" in m.text)
async def uc_selected(message: types.Message):
    await message.answer("Promokodni yuboring:")

    dp.register_message_handler(process_promo, content_types=types.ContentTypes.TEXT)

async def process_promo(message: types.Message):
    promo = message.text

    await bot.send_message(CHANNEL_ID,
        f"🆕 UC Sotish\nUser: @{message.from_user.username}\nPromo: {promo}"
    )

    await bot.send_message(ADMIN_ID,
        f"Tasdiqlash kerak:\nUser: {message.from_user.id}\nPromo: {promo}"
    )

    await message.answer("Adminga yuborildi, kuting...")

# 2️⃣ UC SOTIB OLISH
prices_buy = {
    "60 UC": 10000,
    "120 UC": 20000,
    "240 UC": 40000,
    "325 UC": 52000,
    "660 UC": 110000
}

@dp.message_handler(lambda m: m.text == "📥 UC Sotib olish")
async def buy_uc(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for key in prices_buy:
        kb.add(key)
    await message.answer("UC tanlang:", reply_markup=kb)

@dp.message_handler(lambda m: m.text in prices_buy)
async def process_buy(message: types.Message):
    price = prices_buy[message.text]

    cursor.execute("SELECT balance FROM users WHERE user_id=?", (message.from_user.id,))
    balance = cursor.fetchone()[0]

    if balance < price:
        await message.answer("❌ Mablag' yetarli emas")
    else:
        await message.answer("ID raqamingizni yuboring:")
        dp.register_message_handler(lambda msg: finish_buy(msg, price))

async def finish_buy(message: types.Message, price):
    cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id=?",
                   (price, message.from_user.id))
    db.commit()

    await bot.send_message(ADMIN_ID,
        f"🛒 UC sotib olish\nUser: {message.from_user.id}\nID: {message.text}\nSumma: {price}"
    )

    await message.answer("Adminga yuborildi!")

# 3️⃣ HISOB
@dp.message_handler(lambda m: m.text == "💰 Hisob")
async def account(message: types.Message):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (message.from_user.id,))
    balance = cursor.fetchone()[0]

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ To‘ldirish", "➖ Yechish")

    await message.answer(f"Balans: {balance} so'm", reply_markup=kb)

@dp.message_handler(lambda m: m.text == "➕ To‘ldirish")
async def deposit(message: types.Message):
    await message.answer("Kartaga to'lang va screenshot yuboring")

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id,
        caption=f"To'lov screenshot\nUser: {message.from_user.id}"
    )
    await message.answer("Adminga yuborildi")

@dp.message_handler(lambda m: m.text == "➖ Yechish")
async def withdraw(message: types.Message):
    await message.answer("Karta raqam yuboring (min 15000)")

    dp.register_message_handler(process_withdraw)

async def process_withdraw(message: types.Message):
    await bot.send_message(ADMIN_ID,
        f"Pul yechish\nUser: {message.from_user.id}\nKarta: {message.text}"
    )
    await message.answer("Adminga yuborildi")

# 4️⃣ YORDAM
@dp.message_handler(lambda m: m.text == "🆘 Yordam")
async def help_section(message: types.Message):
    await message.answer("Muammoingizni yozing:")

    dp.register_message_handler(send_to_admin)

async def send_to_admin(message: types.Message):
    await bot.send_message(ADMIN_ID,
        f"Yordam:\nUser: {message.from_user.id}\nText: {message.text}"
    )
    await message.answer("Yuborildi")

# RUN
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
