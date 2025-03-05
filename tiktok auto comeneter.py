import time
import json
import random
import threading
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

driver = None  # Global driver

def load_cookies():
    global driver
    try:
        with open("tiktok_cookies.json", "r") as f:
            cookies = json.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        status_label.config(text="✅ Cookies dimuat, login berhasil", fg="lightgreen")
        time.sleep(2)  # Tunggu sebentar agar halaman benar-benar siap
        go_to_livestream()  # Langsung ke live tanpa menunggu
    except Exception:
        status_label.config(text="⚠️ Gagal memuat cookies", fg="orange")

def start_browser():
    threading.Thread(target=run_browser, daemon=True).start()

def run_browser():
    global driver
    chrome_options = Options()
    
    if browser_mode.get() == "Headless":
        chrome_options.add_argument("--headless")

    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=chrome_options)
    
    status_label.config(text="🌐 Membuka TikTok...", fg="white")
    driver.get("https://www.tiktok.com/")
    load_cookies()  # Load cookies langsung

def go_to_livestream():
    livestream_url = entry_url.get()
    if not livestream_url:
        messagebox.showerror("Error", "Masukkan URL livestream")
        return

    status_label.config(text="📡 Memuat halaman live...", fg="white")
    threading.Thread(target=load_livestream, args=(livestream_url,), daemon=True).start()

def load_livestream(livestream_url):
    global driver
    try:
        driver.get(livestream_url)
        time.sleep(3)  # Tunggu sebentar agar halaman benar-benar termuat
        for _ in range(5):  # Cek 5x dengan delay 1 detik agar lebih stabil
            if driver.find_elements(By.XPATH, "//*[@id='tiktok-live-main-container-id']"):
                status_label.config(text="✅ Halaman live berhasil dimuat", fg="lightgreen")
                return
            time.sleep(1)
        status_label.config(text="❌ Gagal memuat halaman live", fg="red")
    except:
        status_label.config(text="❌ Error saat memuat halaman live", fg="red")

def refresh_browser():
    if driver:
        status_label.config(text="🔄 Memuat halaman live...", fg="white")  # Status langsung berubah
        
        driver.refresh()
        time.sleep(3)  # Tunggu sejenak untuk memastikan refresh selesai
        
        # Cek apakah halaman live berhasil dimuat
        for _ in range(5):  # Cek 5x dengan delay 1 detik agar lebih stabil
            if driver.find_elements(By.XPATH, "//*[@id='tiktok-live-main-container-id']"):
                status_label.config(text="✅ Halaman live berhasil dimuat", fg="lightgreen")
                return
            time.sleep(1)
        
        status_label.config(text="❌ Gagal memuat halaman live", fg="red")
    else:
        messagebox.showerror("Error", "Browser belum dibuka!")


def start_commenting():
    if driver is None:
        messagebox.showerror("Error", "Buka browser terlebih dahulu!")
        return
    
    comment_text = entry_comment.get()
    try:
        delay = int(entry_delay.get())
    except ValueError:
        messagebox.showerror("Error", "Masukkan angka yang valid untuk delay")
        return
    
    if not comment_text:
        messagebox.showerror("Error", "Masukkan komentar terlebih dahulu")
        return

    while loop_var.get():
        try:
            comment_box = driver.find_element(By.XPATH, "//*[@id='tiktok-live-main-container-id']/div[3]/div/div[2]/div/div[2]/div[3]/div[4]/div[1]/div/div[1]/div")
            # Simulasi scrolling atau klik area lain secara acak sebelum berkomentar
            if random.random() > 0.5:
                driver.execute_script("window.scrollBy(0, random.randint(-50, 50))")
                time.sleep(random.uniform(0.5, 1.5))  # Delay acak sebelum mengetik
            comment_box.click()
            time.sleep(random.uniform(delay - 1, delay + 1))
            for char in comment_text:
                comment_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))  # Simulasi mengetik per karakter

            time.sleep(random.uniform(0.5, 1.5))  # Delay sebelum menekan Enter
            comment_box.send_keys(Keys.ENTER) 
            status_label.config(text=f"💬 Komentar terkirim: {comment_text}", fg="lightblue")

            # Tunggu 1 detik sebelum status berubah
            time.sleep(1)
            status_label.config(text="⏳ Menunggu delay...", fg="yellow")

            # Delay countdown
            for i in range(delay, -1, -1):
                countdown_label.config(text=f"⏳ Delay: {i} detik")
                root.update()
                time.sleep(1)
        except:
            time.sleep(random.uniform(1.5, 3.0))  # Tunggu sebentar sebelum mulai pengecekan

            # Coba cek komentar hingga 5 detik sebelum menganggap gagal
            timeout = 5  
            start_time = time.time()

            while time.time() - start_time < timeout:
                latest_comments = driver.find_elements(By.XPATH, "//div[contains(@class, 'chat-message-class')]")
                
                if latest_comments and comment_text in latest_comments[-1].text:
                    status_label.config(text=f"✅ Komentar berhasil terkirim: {comment_text}", fg="lightgreen")
                    break  # Keluar dari loop jika sudah ditemukan
                
                time.sleep(1)  # Cek ulang tiap 1 detik

            else:
                status_label.config(text="⚠️ Komentar mungkin terkirim tetapi tidak terdeteksi", fg="orange")

def toggle_commenting():
    if loop_var.get():
        loop_var.set(False)
        btn_toggle.config(text="Start", **btn_style_start)
    else:
        loop_var.set(True)
        btn_toggle.config(text="Stop", **btn_style_stop)
        threading.Thread(target=start_commenting, daemon=True).start()

root = tk.Tk()
root.title("TikTok Auto Commenter")
root.geometry("500x550")
root.configure(bg="#1e1e2d")

label_style = {"bg": "#1e1e2d", "fg": "white", "font": ("Arial", 11, "bold")}
input_style = {"bg": "#2e2e3e", "fg": "white", "insertbackground": "white", "font": ("Arial", 11), "bd": 0, "relief": "flat"}
btn_style_start = {"bg": "#4CAF50", "fg": "white", "font": ("Arial", 11, "bold"), "bd": 0, "width": 20, "height": 2}
btn_style_stop = {"bg": "#FF3B3B", "fg": "white", "font": ("Arial", 11, "bold"), "bd": 0, "width": 20, "height": 2}
btn_style_refresh = {"bg": "#FFA500", "fg": "white", "font": ("Arial", 11, "bold"), "bd": 0, "width": 5, "height": 2}

# Frame Status dengan Desain Lebih Estetik
status_frame = tk.Frame(root, bg="#2e2e3e", bd=3, relief="ridge")
status_frame.pack(pady=10, padx=10, fill="x")

status_label = tk.Label(status_frame, text="🔄 Menunggu aksi...", **label_style)
status_label.pack(pady=10, padx=10)

browser_mode = tk.StringVar(value="Normal")
tk.Label(root, text="Mode Browser:", **label_style).pack()
tk.Radiobutton(root, text="Normal", variable=browser_mode, value="Normal", bg="#1e1e2d", fg="white", selectcolor="#1e1e2d", font=("Arial", 11)).pack()
tk.Radiobutton(root, text="Headless", variable=browser_mode, value="Headless", bg="#1e1e2d", fg="white", selectcolor="#1e1e2d", font=("Arial", 11)).pack()

def create_input_field(label_text, entry_var, width=50):
    tk.Label(root, text=label_text, **label_style).pack(pady=5, anchor="w", padx=10)
    entry = tk.Entry(root, textvariable=entry_var, width=width, **input_style)
    entry.pack(pady=2, ipadx=5, ipady=5, padx=10)
    return entry

entry_url_var = tk.StringVar()
entry_url = create_input_field("Masukkan URL Livestream:", entry_url_var)

# Frame untuk tombol browser, refresh, dan go
browser_frame = tk.Frame(root, bg="#1e1e2d")
browser_frame.pack(pady=(10, 5))

tk.Button(browser_frame, text="Mulai Browser", command=start_browser, **btn_style_start).pack(side="left", padx=5)
tk.Button(browser_frame, text="🔄", command=refresh_browser, **btn_style_refresh).pack(side="left", padx=5)  # Tombol Refresh

# Tombol "Go" dengan warna biru dan ikon di tengah
btn_style_go = {"bg": "#007BFF",  "fg": "white","font": ("Arial", 11, "bold"), "bd": 0,"width": 5,"height": 2}
tk.Button(browser_frame, text="▶", command=go_to_livestream, **btn_style_go).pack(side="left", padx=5)  # Tombol Go

entry_comment_var = tk.StringVar()
entry_comment = create_input_field("Masukkan Komentar:", entry_comment_var, width=50)

entry_delay_var = tk.StringVar()
entry_delay = create_input_field("Masukkan Delay (detik):", entry_delay_var, width=10)

loop_var = tk.BooleanVar()
loop_var.set(False)

countdown_label = tk.Label(root, text="", **label_style)
countdown_label.pack(pady=5)

btn_toggle = tk.Button(root, text="Start", command=toggle_commenting, **btn_style_start)
btn_toggle.pack(pady=10)

root.mainloop()
