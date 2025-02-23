import logging
import os
import yt_dlp
import instaloader
from tiktokapipy.api import TikTokAPI
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создаем папку для загрузок, если её нет
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Функция для скачивания видео с YouTube
def download_video(url: str):
    options = {
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "video")
        file_path = ydl.prepare_filename(info)
        return file_path, title

# Функция для скачивания фото из Instagram
def download_instagram_photo(url: str):
    loader = instaloader.Instaloader(dirname_pattern=DOWNLOAD_DIR, filename_pattern="{shortcode}")
    try:
        shortcode = url.split("/")[-2]
        loader.download_post(instaloader.Post.from_shortcode(loader.context, shortcode), target=DOWNLOAD_DIR)
        for file in os.listdir(DOWNLOAD_DIR):
            if file.startswith(shortcode) and file.endswith(".jpg"):
                return os.path.join(DOWNLOAD_DIR, file)
    except Exception as e:
        logging.error(f"Ошибка при скачивании фото Instagram: {e}")
        return None

# Функция для скачивания видео из TikTok
def download_tiktok(url: str):
    try:
        with TikTokAPI() as api:
            video = api.video(url)
            video_path = os.path.join(DOWNLOAD_DIR, f"{video.id}.mp4")
            with open(video_path, "wb") as f:
                f.write(video.bytes())
            return video_path
    except Exception as e:
        logging.error(f"Ошибка при скачивании TikTok: {e}")
        return None

# Обработчик сообщений с ссылками
@dp.message(lambda message: message.text)
async def handle_message(message: Message):
    url = message.text

    # Получаем информацию о пользователе
    user_info = (
        f"👤 **Информация о пользователе:**\n"
        f"🔹 ID: `{message.from_user.id}`\n"
        f"🔹 Username: @{message.from_user.username if message.from_user.username else 'Нет'}\n"
        f"🔹 Имя: {message.from_user.first_name}\n"
        f"🔹 Фамилия: {message.from_user.last_name if message.from_user.last_name else 'Нет'}\n"
        f"🔹 Язык: {message.from_user.language_code}\n"
        f"🔹 Чат ID: `{message.chat.id}`\n"
        f"🔹 Чат тип: {message.chat.type}\n"
        f"🔹 Бот?: {'Да' if message.from_user.is_bot else 'Нет'}\n"
        f"🔹 Ссылка для скачивания: {url}"
    )

    # Отправляем админу информацию о пользователе
    if ADMIN_ID:
        await bot.send_message(ADMIN_ID, user_info, parse_mode="Markdown")

    if "instagram.com/p/" in url or "instagram.com/reel/" in url:
        await message.answer("📷 Скачиваю фото из Instagram...")
        file_path = download_instagram_photo(url)
        if file_path:
            photo = FSInputFile(file_path)
            await message.answer_photo(photo, caption="✅ Ваше фото Instagram")
            os.remove(file_path)
        else:
            await message.answer("❌ Не удалось скачать фото из Instagram.")

    elif "tiktok.com" in url:
        await message.answer("🎥 Скачиваю видео из TikTok...")
        file_path = download_tiktok(url)
        if file_path:
            video = FSInputFile(file_path)
            await message.answer_video(video)
            os.remove(file_path)
        else:
            await message.answer("❌ Ошибка при скачивании TikTok-видео.")

    elif any(site in url for site in ["youtube.com", "youtu.be", "fb.watch"]):
        await message.answer("🔄 Скачиваю видео, подождите...")
        try:
            file_path, title = download_video(url)
            video = FSInputFile(file_path)
            await message.answer_video(video, caption=f"🎬 **{title}**")
            os.remove(file_path)
        except Exception as e:
            logging.error(f"Ошибка при скачивании: {e}")
            await message.answer("❌ Ошибка при скачивании видео.")

    else:
        await message.answer("⚠️ Отправьте ссылку на YouTube, TikTok или Instagram.")

# Функция для админа: список пользователей и загруженных файлов
@dp.message(lambda message: str(message.from_user.id) == ADMIN_ID and message.text == "/admin")
async def admin_panel(message: Message):
    files = os.listdir(DOWNLOAD_DIR)
    file_list = "\n".join(files) if files else "Нет загруженных файлов."
    text = f"👑 **Панель админа**\n📂 Загруженные файлы:\n{file_list}"
    await message.answer(text, parse_mode="Markdown")

# Главная функция
async def main():
    # Отправка уведомления админу о запуске бота
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, "✅ Бот запущен и работает!")
        except Exception as e:
            logging.error(f"Ошибка при отправке уведомления админу: {e}")

    dp.message.register(handle_message)
    dp.message.register(admin_panel)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
