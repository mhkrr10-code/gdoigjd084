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
    # رندر يبحث عن المنفذ 8080 تلقائياً
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

    # التحقق من الإعدادات (اختياري)
    check_config_values()

    # --- جلب التوكن مع تنظيف المسافات ---
    # السطر التالي يسحب التوكن من Render ويحذف أي مسافات مخفية قد تسبب خطأ 401
    env_token = os.environ.get('DISCORD_TOKEN')
    config_token = config['DISCORD'].get('TOKEN')
    
    TOKEN = (env_token or config_token or "").strip()
    
    # ⚠️ خطة الطوارئ: إذا فشل Render في قراءة المتغير، يمكنك وضع التوكن هنا مباشرة بين علامتي التنصيص
    # TOKEN = "ضع_التوكن_هنا_في_حال_استمرار_المشكلة"

    if TOKEN and len(TOKEN) > 10:
        # أ. تشغيل سيرفر الويب أولاً لفتح المنفذ
        print("🌐 Starting web server on port 8080...")
        keep_alive()
        
        # ب. إنشاء نسخة البوت وتشغيله
        print("🤖 Attempting to login to Discord...")
        try:
            my_bot = Bot(TOKEN, intents)
            my_bot.run(TOKEN)
        except discord.errors.LoginFailure:
            print("❌ ERROR: Login failed! The token provided is INVALID.")
            print("💡 Action: Go to Discord Developer Portal, RESET your token, and update it in Render.")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
    else:
        print("❌ ERROR: No valid Token found! Check DISCORD_TOKEN in Render Environment Variables.")

if(__name__ == '__main__'):
    main()
