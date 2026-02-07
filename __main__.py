import discord
from discord import app_commands
import os
import asyncio
from flask import Flask
from threading import Thread
from bot import *
from config import config as config, check_config_values

# --- 1. سيرفر الويب المصغر لإبقاء البوت حياً في رندر ---
app = Flask('')

@app.route('/')
def home():
    return "✅ Bot is Online and Port is Active!"

def run_web():
    # رندر يبحث عن المنفذ 8080 أو 10000 تلقائياً
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- 2. الدالة الأساسية لتشغيل البوت ---
def main():
    # إعداد الصلاحيات (Intents)
    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    intents.members = True 

    # التحقق من الإعدادات
    missing_values = check_config_values()
    if len(missing_values) > 0:
        print(f'⚠️ Warning: Some config values are missing, checking Environment Variables...')

    # جلب التوكن من رندر (أو من ملف الكوفيج كخيار احتياطي)
    TOKEN = os.environ.get('DISCORD_TOKEN') or config['DISCORD'].get('TOKEN')
    
    if TOKEN and TOKEN != "None":
        # أ. تشغيل سيرفر الويب أولاً لفتح المنفذ
        print("🌐 Starting web server on port 8080...")
        keep_alive()
        
        # ب. إنشاء نسخة البوت وتشغيله
        print("🤖 Logging in to Discord...")
        my_bot = Bot(TOKEN, intents)
        my_bot.run(TOKEN)
    else:
        print("❌ ERROR: No Token found! Make sure DISCORD_TOKEN is set in Render Environment Variables.")

if(__name__ == '__main__'):
    main()
