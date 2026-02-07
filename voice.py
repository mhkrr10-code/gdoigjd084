import threading
import yt_dlp
import discord
import time
import asyncio
import os
from random import shuffle
from song import Song as Song
from song import general_appender, soundcloud_set_appender
from config import config as config
from users import *

class Voice():
    def __init__(self, bot, gid):
        print(f"--- [OK] Voice System Started for Server: {gid} ---")
        self.bot = bot
        self.gid = gid
        self.voice_client = None
        self.current_server = None
        self.is_running = True
        self.songs = []
        self.is_playing = False
        self.is_paused = False
        self.current = None
        self.prefix = config['MESSAGES']['PREFIX']
        self.last_activity_time = time.time()
        self.disconnect_after_idle_time = float(config['DISCORD']['IDLE_TIMEOUT']) * 60
        self.channel = None 

        self.bot.loop.create_task(self.check_idle())

    async def current_song(self):
        if self.current:
            song = self.current
            embed = discord.Embed(
                title=':headphones: Song Playing Now',
                description=f'[{song.name}]({song.url})',
                color=discord.Color.blue()
            )
            embed.add_field(name=f'**Requester:** {song.requested_by}', value='', inline=False)
            await self.channel.send(embed=embed)

    def on_finished_play(self, song, error):
        if error:
            print(f'Playback error: {error}')
        
        self.is_playing = False
        self.current = None
        self.last_activity_time = time.time()
        
        # تشغيل الأغنية التالية تلقائياً
        self.bot.loop.create_task(self.play_next())

    async def play_next(self):
        if len(self.songs) > 0 and not self.is_playing:
            next_song = self.songs.pop(0)
            await self.start_playing(next_song)
        else:
            self.is_playing = False

    async def start_playing(self, song):
        self.is_playing = True
        try:
            # إعدادات الـ FFMPEG لضمان عدم التقطيع
            FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn -ar 48000 -ac 2'
            }

            playback_url = await song.get_playback_url()
            
            # تحديد المسار الكامل لملف ffmpeg.exe الموجود في مجلدك
            # هذا يحل مشكلة Return Code 31999...
            ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg.exe")

            source = discord.FFmpegPCMAudio(
                playback_url,
                executable=ffmpeg_path, 
                **FFMPEG_OPTIONS
            )
            
            self.current = song
            self.voice_client.play(source, after=lambda e: self.on_finished_play(song, e))

            embed = discord.Embed(
                title=':headphones: Song Playing Now',
                description=f'[{song.name}]({song.url})',
                color=discord.Color.blue()
            )
            embed.add_field(name=f'**Requester:** {song.requested_by}', value='', inline=False)
            if self.channel:
                await self.channel.send(embed=embed)
        except Exception as e:
            print(f"Error starting playback: {e}")
            self.is_playing = False
            await self.play_next()

    async def handle_message(self, message):
        if message.author.bot: return
        if not message.content.startswith(self.prefix): return

        self.channel = message.channel
        content = message.content[len(self.prefix):].strip()
        parts = content.split(' ')
        command = parts[0].lower()
        args = ' '.join(parts[1:])

        if command == "join":
            await self.join(message.author, message)
            await message.add_reaction('✅')

        elif command in ["play", "p"]:
            if not args: return
            if self.voice_client is None:
                await self.join(message.author, message)

            requested = args.strip()
            
            # جلب الأغاني
            try:
                if "soundcloud" in requested and "sets" in requested:
                    urls = await soundcloud_set_appender(requested)
                else:
                    urls = await general_appender(requested)

                songs_added = 0
                for url in urls:
                    if url['name'] not in ["[Deleted video]", "[Private video]"]:
                        s = Song(url['url'], url['name'], url['artist'], message.author.display_name, url['duration'])
                        self.songs.append(s)
                        songs_added += 1

                if songs_added > 0:
                    await message.add_reaction('✅')
                    if not self.is_playing:
                        await self.play_next()
                else:
                    await message.add_reaction('❌')
            except Exception as e:
                print(f"Appender Error: {e}")

        elif command == "skip":
            if self.voice_client:
                self.voice_client.stop()
                await message.add_reaction('⏭️')

        elif command == "stop":
            self.songs.clear()
            if self.voice_client: self.voice_client.stop()
            await self.leave()
            await message.add_reaction('⏹️')

        elif command == "about":
            embed = discord.Embed(
                title='MusicBot',
                description='By BuWael & AfterLifeTeam',
                color=discord.Color.blue()
            )
            await self.channel.send(embed=embed)

        elif command in ["q", "queue"]:
            await self.display_queue(message.channel)

    async def display_queue(self, channel):
        if not self.songs and not self.current:
            await channel.send("Queue is empty!")
            return
        
        q_text = f"**Now Playing:** {self.current.name}\n\n" if self.current else ""
        for i, s in enumerate(self.songs[:10], 1):
            q_text += f"{i}. {s.name}\n"
        
        embed = discord.Embed(title="Song Queue", description=q_text, color=discord.Color.blue())
        await channel.send(embed=embed)

    async def join(self, author, message):
        if not author.voice:
            await message.channel.send("❌ You must be in a voice channel!")
            return
        if self.voice_client is None:
            self.voice_client = await author.voice.channel.connect(self_deaf=True)
            self.current_server = author.voice.channel
        else:
            await self.voice_client.move_to(author.voice.channel)

    async def leave(self):
        if self.voice_client:
            await self.voice_client.disconnect()
        self.voice_client = None
        self.is_playing = False
        self.current = None

    async def check_idle(self):
        while self.is_running:
            await asyncio.sleep(15)
            if self.voice_client and not self.is_playing and time.time() - self.last_activity_time > self.disconnect_after_idle_time:
                await self.leave()
                break