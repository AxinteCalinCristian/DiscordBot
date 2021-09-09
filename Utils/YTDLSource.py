import asyncio
import discord
import datetime

class YTDLSource(discord.PCMVolumeTransformer):
    _data = None
    _title = None
    _url = None
    _ffmpeg_options = None

    def __init__(self, src, is_playlist=False, *, playlist_url='', data, volume=0.5):
        super().__init__(src, volume)

        self._data = data
        if not is_playlist:
            self._title = data.get('title')
            self._url = data.get('url')
            if 'duration' in data:
                self._duration = str(datetime.timedelta(seconds=data['duration']))
            else:
                self._duration = 0
        else:
            self._playlist_url = playlist_url
            self._title = data['entries'][0]['playlist']
            self._songs = data['entries']

    @classmethod
    async def fromUrl(cls, url, ytld, ffmpeg_options, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytld.extract_info(url, download=not stream))

        if '_type' in data and data['_type'] == 'playlist':
            is_playlist = True
        else:
            is_playlist = False

        if not is_playlist:
            if 'entries' in data:
                data = data['entries'][0]

            filename = data['url'] if stream else ytld.prepare_filename(data)
        else:
            filename = url if stream else ytld.prepare_filename(data)

        return cls(discord.FFmpegPCMAudio(source=filename, **ffmpeg_options,
                                          executable="./ffmpeg/bin/ffmpeg.exe",), is_playlist=is_playlist, playlist_url=url, data=data)

    def getPlaylistSongs(self):
        songs = []
        for song in self._songs:
            songs.append({'name': song.get('title'), 'url': song.get('url'), 'duration': str(datetime.timedelta(seconds=song.get('duration')))})

        return songs

    def getPlaylistUrl(self):
        return self._playlist_url

    def getPlaylistName(self):
        return self._title

    def getSongName(self):
        return self._title

    def getSongDuration(self):
        return self._duration
