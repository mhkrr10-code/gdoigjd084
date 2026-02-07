from bot import *
from config import config as config, check_config_values
import discord
import os # أضفنا هذا السطر

def main():
    # إعداد الصلاحيات (Intents)
    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    intents.members = True 

    missing_values = check_config_values()
    if len(missing_values) > 0:
        # ملاحظة: التوكن الآن سيسحب من رندر، لذا لن يعتبر مفقوداً حتى لو كان الملف فارغاً
        print(f'Checking config file, but will also look in Environment Variables...')

    # --- التعديل هنا لسحب التوكن من رندر ---
    TOKEN = os.environ.get('DISCORD_TOKEN') or config['DISCORD'].get('TOKEN')
    
    if TOKEN and TOKEN != "None":
        # إنشاء نسخة البوت
        my_bot = Bot(TOKEN, intents)
        
        # تشغيل البوت
        my_bot.run(TOKEN)
    else:
        print("❌ ERROR: No Token found! Please set DISCORD_TOKEN in Render Environment Variables.")

if(__name__ == '__main__'):
    main()