import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv

from instagram import download_instagram_content
from tiktok import download_tiktok
from youtube import download_video

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Включаем логирование
logging.basicConfig(level=logging.DEBUG)

# Создаем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создаем папку для загрузок, если её нет
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Функция экранирования MarkdownV2
def escape_markdown(text: str) -> str:
    escape_chars = '_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

# Обработчик сообщений с ссылками
@dp.message(lambda message: message.text)
async def handle_message(message: Message):
    url = message.text

    # Получаем информацию о пользователе
    user_info = (
        f"\U0001F464 *Информация о пользователе:*\n"
        f"🔹 *ID:* {message.from_user.id}\n"
        f"🔹 *Username:* @{message.from_user.username if message.from_user.username else 'Нет'}\n"
        f"🔹 *Имя:* {message.from_user.first_name}\n"
        f"🔹 *Язык:* {message.from_user.language_code}\n"
        f"🔹 *Ссылка:* {url}"
    )
    user_info = escape_markdown(user_info)

    # Отправляем админу информацию о пользователе
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, user_info, parse_mode="MarkdownV2")
        except Exception as e:
            logging.error(f"Ошибка при отправке админу: {e}")

    if "instagram.com" in url:
        await message.answer("📥 Скачиваю контент из Instagram...")
        file_path = download_instagram_content(url)
        if file_path:
            if file_path.endswith(".jpg"):
                await message.answer_photo(FSInputFile(file_path), caption="✅ Ваше фото Instagram")
            elif file_path.endswith(".mp4"):
                await message.answer_video(FSInputFile(file_path), caption="✅ Ваше видео Instagram")
            os.remove(file_path)
        else:
            await message.answer("❌ Не удалось скачать контент из Instagram.")


    elif "tiktok.com" in url:
        await message.answer("🎥 Скачиваю видео из TikTok через SnapTik...")
        file_path = download_tiktok(url)
        if file_path:
            await message.answer_video(FSInputFile(file_path), caption="✅ Ваше видео TikTok")
            os.remove(file_path)
        else:
            await message.answer("❌ Ошибка при скачивании TikTok-видео.")


    elif "youtube.com" in url or "youtu.be" in url:
        await message.answer("🔄 Скачиваю видео, подождите...")
        try:
            file_path, title = download_video(url)
            title = escape_markdown(title)
            await message.answer_video(FSInputFile(file_path), caption=f"🎬 *{title}*", parse_mode="MarkdownV2")
            os.remove(file_path)
        except Exception as e:
            logging.error(f"Ошибка при скачивании: {e}")
            await message.answer("❌ Ошибка при скачивании видео.")

    else:
        await message.answer("⚠️ Отправьте ссылку на YouTube, TikTok или Instagram.")

# Запуск бота
async def main():
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, "✅ Бот запущен и работает!", parse_mode="MarkdownV2")
        except Exception as e:
            logging.error(f"Ошибка при отправке админу: {e}")

    dp.message.register(handle_message)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())