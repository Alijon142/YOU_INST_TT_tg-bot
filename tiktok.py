import os
import logging
import yt_dlp

download_dir = "downloads"
os.makedirs(download_dir, exist_ok=True)

# Путь к файлу с куками TikTok
COOKIES_FILE = "tiktok_com_cookies.txt"

def download_tiktok(url: str):
    options = {
        'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'merge_output_format': 'mp4',
        'cookies': COOKIES_FILE,  # Используем куки
    }
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "tiktok_video")
            file_path = ydl.prepare_filename(info)
            return file_path
    except Exception as e:
        logging.error(f"Ошибка при скачивании TikTok-видео: {e}")
        return None
