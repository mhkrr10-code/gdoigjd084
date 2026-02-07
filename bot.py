import discord
from discord import app_commands
from config import config as config
from song import Song as Song
import asyncio
from voice import Voice as Voice
import os # أضفنا هذا السطر فقط لاستخدام مكتبة النظام

class Bot(discord.Client):
    def __init__(self, TOKEN, INTENTS):
        super().__init__(intents=INTENTS)
        self.TOKEN = TOKEN
        self.voice_connections = []
        self.song_queue = {}
        self.version = 1.1
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # تسجيل الأوامر في شجرة البوت
        self.tree.add_command(play_slash)
        self.tree.add_command(skip_slash)
        self.tree.add_command(stop_slash)
        self.tree.add_command(queue_slash)
        self.tree.add_command(shuffle_slash)
        self.tree.add_command(clear_slash)
        self.tree.add_command(help_slash)
        self.tree.add_command(about_slash)
        self.tree.add_command(move_slash)
        
        # مزامنة الأوامر مع خوادم ديسكورد
        await self.tree.sync()

    def get_voice_handler(self, guild_id):
        v = None
        for vc in self.voice_connections:
            if vc.gid == guild_id:
                v = vc
                break
        if v is None:
            v = Voice(self, guild_id)
            self.voice_connections.append(v)
            if guild_id in self.song_queue:
                v.songs = self.song_queue[guild_id]
        return v

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
        self.loop.create_task(self.play_task())

    async def play_task(self):
        await self.wait_until_ready()
        while not self.is_closed():
            await asyncio.sleep(0.5)
            for vc in self.voice_connections:
                if vc.voice_client and vc.voice_client.is_connected():
                    if(len(vc.songs) > 0 and not vc.voice_client.is_playing() and not vc.is_paused):
                        s = vc.songs.pop(0)
                        await vc.start_playing(s)

# --- تعريف الأوامر كمجموعة Slash Commands ---

@app_commands.command(name="play", description="Play a song or link")
async def play_slash(interaction: discord.Interaction, search: str):
    await interaction.response.send_message(f"🔍 Searching for: **{search}**")
    v = interaction.client.get_voice_handler(interaction.guild_id)
    await v.handle_message(MockMsg(interaction, f"play {search}"))

@app_commands.command(name="skip", description="Skip the current song")
async def skip_slash(interaction: discord.Interaction):
    await interaction.response.send_message("⏭️ Song skipped")
    v = interaction.client.get_voice_handler(interaction.guild_id)
    await v.handle_message(MockMsg(interaction, "skip"))

@app_commands.command(name="stop", description="Stop music and disconnect")
async def stop_slash(interaction: discord.Interaction):
    await interaction.response.send_message("🛑 Stopped")
    v = interaction.client.get_voice_handler(interaction.guild_id)
    await v.handle_message(MockMsg(interaction, "stop"))

@app_commands.command(name="queue", description="Display the current song queue")
async def queue_slash(interaction: discord.Interaction, page: int = 1):
    await interaction.response.send_message(f"📜 Getting queue page {page}...")
    v = interaction.client.get_voice_handler(interaction.guild_id)
    await v.handle_message(MockMsg(interaction, f"queue {page}"))

@app_commands.command(name="shuffle", description="Shuffle the song queue")
async def shuffle_slash(interaction: discord.Interaction):
    await interaction.response.send_message("🔀 Shuffling...")
    v = interaction.client.get_voice_handler(interaction.guild_id)
    await v.handle_message(MockMsg(interaction, "shuffle"))

@app_commands.command(name="clear", description="Clear all songs from queue")
async def clear_slash(interaction: discord.Interaction):
    await interaction.response.send_message("🧹 Queue cleared")
    v = interaction.client.get_voice_handler(interaction.guild_id)
    await v.handle_message(MockMsg(interaction, "clear"))

@app_commands.command(name="move", description="Move a song in queue")
@app_commands.describe(index1="From position", index2="To position")
async def move_slash(interaction: discord.Interaction, index1: int, index2: int):
    await interaction.response.send_message(f"🚚 Moving song from {index1} to {index2}")
    v = interaction.client.get_voice_handler(interaction.guild_id)
    await v.handle_message(MockMsg(interaction, f"move {index1} {index2}"))

@app_commands.command(name="help", description="Show all available commands")
async def help_slash(interaction: discord.Interaction):
    await interaction.response.send_message("📖 Commands Menu:")
    v = interaction.client.get_voice_handler(interaction.guild_id)
    await v.display_help(interaction.channel)

@app_commands.command(name="about", description="About this bot")
async def about_slash(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True) 
    v = interaction.client.get_voice_handler(interaction.guild_id)
    await v.handle_message(MockMsg(interaction, "about"))

class MockMsg:
    def __init__(self, interaction, content):
        self.content = f"{config['MESSAGES']['PREFIX']}{content}"
        self.author = interaction.user
        self.channel = interaction.channel
        self.guild = interaction.guild
        self.is_slash = True
    async def add_reaction(self, emoji): pass

# --- التعديل المطلوب هنا فقط لربط التوكن بـ Render ---
if __name__ == "__main__":
    # يسحب التوكن من Environment Variables في Render
    TOKEN = os.environ.get('DISCORD_TOKEN')
    
    if TOKEN:
        intents = discord.Intents.all()
        client = Bot(TOKEN=TOKEN, INTENTS=intents)
        client.run(TOKEN)
    else:
        print("❌ لم يتم العثور على التوكن في إعدادات Render!")