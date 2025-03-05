import json
import time
from selenium import webdriver

# Setup driver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-webrtc")
driver = webdriver.Chrome(options=options)

# Buka TikTok Login Page
driver.get("https://www.tiktok.com/login")

# Tunggu pengguna login secara manual
input("Login ke TikTok, lalu tekan Enter untuk menyimpan cookies...")

# Simpan cookies setelah login
cookies = driver.get_cookies()
with open("tiktok_cookies.json", "w") as f:
    json.dump(cookies, f)

print("Cookies berhasil disimpan!")
driver.quit()
