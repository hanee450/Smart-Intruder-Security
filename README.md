# 🛡️ Smart Webcam Intruder Security System

Computer vision par aadharit security tool jo aapke webcam ko Desk Surveillance System mein badal deta hai. Jab bhi koi insaan aapke desk ke paas aayega, yeh automatically unka photo capture karke aapke **Telegram App** par instant notification aur photo bhej dega.

---

### 🚀 Quick Setup Instructions:

#### 1. Telegram Bot Setup (Free & Easy - 2 Minutes):
1. Telegram app open karein aur search karein `@BotFather`.
2. Send command: `/newbot`.
3. Apne bot ka name aur username rakhein (e.g. `MyHomeSecurityBot`).
4. `@BotFather` aapko ek **API Token** dega (e.g. `123456789:ABCdefGHIjklmNOP...`).
5. Ab Telegram par `@userinfobot` search karke `/start` karein, yeh aapko aapki **Chat ID** bata dega (e.g. `987654321`).

#### 2. Config File Update:
Open [config.json](file:///C:/Users/Honey%20Mishra/.gemini/antigravity/scratch/IntruderSystem/config.json) and enter your Telegram credentials:
```json
{
    "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN_HERE",
    "telegram_chat_id": "YOUR_TELEGRAM_CHAT_ID_HERE"
}
```

---

### 💻 Running the App:

1. Requirements Install Karein:
   ```bash
   pip install -r requirements.txt
   ```

2. App Run Karein:
   ```bash
   python intruder_detector.py
   ```

---

### 🎮 Keyboard Controls:
* **`A`** : Toggle ARM / DISARM (Pause monitoring)
* **`T`** : Send Test Alert Photo to Telegram
* **`Q`** : Quit Application
