from bot import *
from config import config as config, check_config_values
import discord

def main():
    # إعداد الصلاحيات (Intents)
    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    intents.members = True # يفضل تفعيلها للأوامر التفاعلية

    missing_values = check_config_values()
    if len(missing_values) > 0:
        print(f'Missing required options in config file: {missing_values}')
    else:
        TOKEN = config['DISCORD']['TOKEN']
        
        # إنشاء نسخة البوت
        my_bot = Bot(TOKEN, intents)
        
        # تسجيل أوامر السلاش (Slash Commands)
        # ملاحظة: إذا أضفت أوامر جديدة في كلاس Bot، سيتم مزامنتها تلقائياً 
        # بفضل دالة setup_hook التي أضفناها في ملف bot.py السابق.
        
        # تشغيل البوت
        my_bot.run(TOKEN)

if(__name__ == '__main__'):
    main()