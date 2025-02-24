import requests

url = "https://snaptik.app/abc2.php"

headers = {
    "Accept": "*/*",
    "Content-Type": "multipart/form-data",
    "Origin": "https://snaptik.app",
    "Referer": "https://snaptik.app/en2",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
}

data = {
    "url": "https://vt.tiktok.com/ZSMS3kJYK/",
    "lang": "en2",
    "token": "eyMTc0MDM4NjE0Ng==c",
}

response = requests.post(url, headers=headers, data=data)

print(response.text)
