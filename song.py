import os
import time
import asyncio
import json
import yt_dlp

async def soundcloud_set_appender(playlist_url):
    url_list = []
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'ignoreerrors': True,
        'extract_flat': True, # لجلب الروابط فقط دون الدخول في تفاصيل كل أغنية فوراً
        'nocheckcertificate': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # محاولة جلب معلومات القائمة
            info = ydl.extract_info(playlist_url, download=False)

            if info is None:
                info = ydl.extract_info(f"scsearch:{playlist_url}", download=False)

            if 'entries' in info:
                for entry in info['entries']:
                    if entry: # التأكد من أن الإدخال ليس فارغاً
                        url_list.append({
                            'url': entry.get('url') or entry.get('webpage_url'),
                            'name': entry.get('title', "Unknown Title"), 
                            'artist': entry.get('uploader', ""), 
                            'duration': entry.get('duration', 0)
                        })
            else:
                url_list.append({
                    'url': info.get('webpage_url') or info.get('url'), 
                    'name': info.get('title', "Unknown Title"), 
                    'artist': info.get('uploader', ""), 
                    'duration': info.get('duration', 0)
                })

            return url_list
    except Exception as e:
        print(f'SoundCloud Appender Error: {e}')
        return []

async def general_appender(playlist_url):
    url_list = []
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'ignoreerrors': True,
        'extract_flat': 'in_playlist', # مهم جداً لمنع تعليق البوت في القوائم الكبيرة
        'nocheckcertificate': True,
        'default_search': 'auto'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)

            if info is None:
                info = ydl.extract_info(f"ytsearch:{playlist_url}", download=False)

            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        url_list.append({
                            'url': entry.get('url') or entry.get('webpage_url'),
                            'name': entry.get('title', "Unknown Title"), 
                            'artist': entry.get('uploader', ""), 
                            'duration': entry.get('duration', 0)
                        })
            else:
                url_list.append({
                    'url': info.get('webpage_url') or info.get('url'), 
                    'name': info.get('title', "Unknown Title"), 
                    'artist': info.get('uploader', ""), 
                    'duration': info.get('duration', 0)
                })

            return url_list

    except Exception as e:
        print(f'General Appender Error: {e}')
        return []

class Song:
    def __init__(self, url, name="no-title", artist="", requested_by="Noone", duration=0):
        self.duration = duration
        self.name = name
        self.artist = artist
        self.is_ready = False
        self.requested_by = requested_by
        self.url = url
        print(f"--- [Song Added] {self.name} ---")

    async def get_playback_url(self):
        """هذه الدالة تجلب الرابط الحقيقي الذي يفهمه FFMPEG للتشغيل"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'ignoreerrors': True,
            'no_warnings': True,
        }

        try:
            # هنا نستخدم loop.run_in_executor لمنع حظر خيط الـ asyncio الأساسي
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(self.url, download=False))
            
            if info and 'url' in info:
                return info['url']
            return None

        except Exception as e:
            print(f'Error fetching playback URL: {e}')
            return None