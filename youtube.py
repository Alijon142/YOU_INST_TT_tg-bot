import os
import logging
import yt_dlp

download_dir = "downloads"
os.makedirs(download_dir, exist_ok=True)

def download_video(url: str):
    options = {
        'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'merge_output_format': 'mp4',
    }
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "video")
            file_path = ydl.prepare_filename(info)
            return file_path, title
    except Exception as e:
        logging.error(f"Ошибка при скачивании YouTube-видео: {e}")
        return None, None
