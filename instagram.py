import os
import logging
import instaloader
import requests
import re

download_dir = "downloads"
os.makedirs(download_dir, exist_ok=True)


def get_shortcode(url: str):
    """Функция для получения шорткода из ссылки"""
    try:
        response = requests.get(url, allow_redirects=True)
        if response.status_code == 200:
            return response.url.split("/")[-2]
    except Exception as e:
        logging.error(f"Ошибка при получении шорткода: {e}")
    return None


def download_instagram_content(url: str):
    """Скачивает фото или видео с Instagram."""
    loader = instaloader.Instaloader(dirname_pattern=download_dir, filename_pattern="{shortcode}")
    try:
        shortcode = get_shortcode(url) if "share" in url else url.split("/")[-2]
        if not shortcode:
            logging.error("Не удалось получить шорткод.")
            return None

        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        if post.is_video:
            return download_instagram_video(post.video_url, shortcode)
        else:
            loader.download_post(post, target=download_dir)
            for file in os.listdir(download_dir):
                if file.startswith(shortcode) and file.endswith(".jpg"):
                    return os.path.join(download_dir, file)
    except Exception as e:
        logging.error(f"Ошибка при скачивании контента Instagram: {e}")
        return None


def download_instagram_video(video_url: str, shortcode: str):
    """Скачивает видео из Instagram."""
    try:
        video_path = os.path.join(download_dir, f"{shortcode}.mp4")
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(video_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return video_path
        else:
            logging.error(f"Ошибка загрузки видео: {response.status_code}")
    except Exception as e:
        logging.error(f"Ошибка при скачивании видео Instagram: {e}")
    return None
