import discord
import os
import asyncio
from flask import Flask
from threading import Thread
from bot import Bot # تأكد أن الكلاس مكتوب بـ Bot كبير

# --- 1. سيرفر الويب (شغال تمام عندك) ---
app = Flask('')
@app.route('/')
def home(): return "✅ Bot is Online"

def run_web(): app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- 2. تشغيل البوت ---
def main():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    intents.members = True 

    # --- إجبار البوت على قراءة التوكن من رندر فقط وتجاهل أي ملفات أخرى ---
    TOKEN = os.environ.get('DISCORD_TOKEN', '').strip()
    
    # تحذير بسيط في السجلات لو التوكن طار
    if not TOKEN:
        print("❌ CRITICAL ERROR: DISCORD_TOKEN variable is EMPTY in Render settings!")
        return

    print(f"🌐 Web server starting...")
    keep_alive()
    
    print(f"🤖 Attempting login with token length: {len(TOKEN)}") # سطر للتأكد من وجود التوكن
    
    try:
        # ملاحظة: استبدلنا my_bot = Bot(TOKEN, intents) بـ النسخة المباشرة
        client = Bot(TOKEN, intents)
        client.run(TOKEN)
    except discord.errors.LoginFailure:
        print("❌ ERROR: Discord rejected the token! (401 Unauthorized)")
        print("💡 QUICK FIX: Go to Discord Developers -> Bot -> Reset Token. Copy the NEW one to Render.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if(__name__ == '__main__'):
    main()
