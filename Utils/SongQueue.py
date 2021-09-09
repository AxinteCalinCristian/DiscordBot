import asyncio
import json
import discord
from emoji import EMOJI_ALIAS_UNICODE_ENGLISH as EMOJIS

from discord.utils import get
from Utils.YoutubeManager import YoutubeManager
from Utils.clearAudioFilesFolder import deleteAudioFiles


class SongQueue:
    _queue = []
    _loop = False
    _ctx = None
    _client = None
    _currentSongIndex = 0

    # MESSAGES

    @staticmethod
    async def messageSongPlaying(song):
        embed = discord.Embed(title=song['name'], url=song['url'],
                              color=0x63b7f2)
        embed.set_author(name='Now playing',
                         icon_url=SongQueue._ctx.author.avatar_url)
        embed.add_field(name="Duration", value=str(song['duration']), inline=True)
        embed.add_field(name="Position in queue", value=str(SongQueue._currentSongIndex + 1) + '/' +
                                                        str(len(SongQueue._queue)), inline=True)
        await SongQueue._ctx.channel.send(embed=embed)

    @staticmethod
    async def messageSongAdded(song):
        embed = discord.Embed(title=song['name'], url=song['url'],
                              color=0x18b549)
        embed.set_author(name='Added to queue',
                         icon_url=SongQueue._ctx.author.avatar_url)
        embed.add_field(name="Duration", value=str(song['duration']), inline=True)
        embed.add_field(name="Position in queue", value=str(len(SongQueue._queue)) + '/' +
                                                        str(len(SongQueue._queue)), inline=True)
        await SongQueue._ctx.channel.send(embed=embed)

    @staticmethod
    async def messageSongRemoved(song):
        embed = discord.Embed(title=song['name'], url=song['url'],
                              color=0xb00e09)
        embed.set_author(name='Deleted from queue',
                         icon_url=SongQueue._ctx.author.avatar_url)
        await SongQueue._ctx.channel.send(embed=embed)

    @staticmethod
    async def messageSongPaused(song):
        embed = discord.Embed(title=song['name'], url=song['url'],
                              color=0x0c0c87)
        embed.set_author(name='Song paused',
                         icon_url=SongQueue._ctx.author.avatar_url)
        embed.add_field(name="Duration", value=str(song['duration']), inline=True)
        embed.add_field(name="Position in queue", value=str(SongQueue._currentSongIndex) + '/' +
                                                        str(len(SongQueue._queue)), inline=True)
        await SongQueue._ctx.channel.send(embed=embed)

    @staticmethod
    async def messageSongResumed(song):
        embed = discord.Embed(title=song['name'], url=song['url'],
                              color=0x920bd6)
        embed.set_author(name='Song resumed',
                         icon_url=SongQueue._ctx.author.avatar_url)
        embed.add_field(name="Duration", value=str(song['duration']), inline=True)
        embed.add_field(name="Position in queue", value=str(SongQueue._currentSongIndex) + '/' +
                                                        str(len(SongQueue._queue)), inline=True)
        await SongQueue._ctx.channel.send(embed=embed)

    @staticmethod
    async def messageSongSkipped(song):
        embed = discord.Embed(title=song['name'], url=song['url'],
                              color=0xf74514)
        embed.set_author(name='Song skipped',
                         icon_url=SongQueue._ctx.author.avatar_url)
        embed.add_field(name="Duration", value=str(song['duration']), inline=True)
        embed.add_field(name="Position in queue", value=str(SongQueue._currentSongIndex) + '/' +
                                                        str(len(SongQueue._queue)), inline=True)
        await SongQueue._ctx.channel.send(embed=embed)

    @staticmethod
    async def messageLoopQueueStatus():
        if SongQueue._loop:
            embed = discord.Embed(title="Now looping the queue",
                                  color=0xbcd40d)
            await SongQueue._ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(title="Stopped looping the queue",
                                  color=0xbcd40d)
            await SongQueue._ctx.channel.send(embed=embed)

    @staticmethod
    async def displayQueue():
        embed = discord.Embed(title=f'Queue for {SongQueue._ctx.message.guild.name}',
                              color=0xed34e4)

        content = ''
        idx = 1
        for song in SongQueue._queue:
            song_name = song['name']
            song_url = song['url']
            requester = song['requester']
            duration = song['duration']

            content += f"`{idx}.` {song_name}  |  `{duration}`\n`Requested by {requester}\n`"
            if idx < len(SongQueue._queue):
                content += '\n'

            idx += 1

        embed.description = content
        if SongQueue._loop:
            status_emoji = EMOJIS[':white_check_mark:']
        else:
            status_emoji = EMOJIS[':x:']
        embed.set_footer(text=f'Loop queue: {status_emoji}')

        await SongQueue._ctx.channel.send(embed=embed)

    @staticmethod
    async def addedPlaylistToQueue(playlist):
        embed = discord.Embed(title=playlist['name'], url=playlist['url'],
                              color=0x18b549)
        embed.set_author(name='Added playlist to queue',
                         icon_url=SongQueue._ctx.author.avatar_url)
        await SongQueue._ctx.channel.send(embed=embed)

    @staticmethod
    async def sendErrorMessage(msg):
        embed = discord.Embed(title=msg,
                              color=0x344245)

        await SongQueue._ctx.channel.send(embed=embed)

    # ACTIONS

    @staticmethod
    def setCtx(ctx):
        SongQueue._ctx = ctx

    @staticmethod
    def setClient(client):
        SongQueue._client = client

    @staticmethod
    async def addSong(song):
        server = SongQueue._ctx.message.guild
        voice_channel = server.voice_client
        if not voice_channel.is_playing():
            SongQueue._queue.append(song)
            await SongQueue.messageSongAdded(song)
            await SongQueue.playSong()
        else:
            SongQueue._queue.append(song)
            await SongQueue.messageSongAdded(song)

    @staticmethod
    async def addPlaylist(playlist):
        for song in playlist['songs']:
            SongQueue._queue.append(song)

        await SongQueue.addedPlaylistToQueue(playlist)

        server = SongQueue._ctx.message.guild
        voice_channel = server.voice_client
        if not voice_channel.is_playing():
            await SongQueue.playSong()

    @staticmethod
    async def deleteSong(index):
        if not index.isnumeric():
            await SongQueue.sendErrorMessage("Please provide a valid index")
        elif index.isnumeric() and int(index) < 1 or int(index) > len(SongQueue._queue):
            await SongQueue.sendErrorMessage("Please provide a valid index")

        index = int(index) - 1
        await SongQueue.messageSongRemoved(SongQueue._queue[index])
        voice_channel = get(SongQueue._ctx.bot.voice_clients, guild=SongQueue._ctx.guild)

        if SongQueue._currentSongIndex > index:
            SongQueue._currentSongIndex -= 1

        if voice_channel.is_playing() and SongQueue._currentSongIndex == index:
            voice_channel.stop()

        del SongQueue._queue[index]

    @staticmethod
    async def playSong():
        if SongQueue._currentSongIndex < len(SongQueue._queue):
            voice_channel = get(SongQueue._ctx.bot.voice_clients, guild=SongQueue._ctx.guild)

            song = SongQueue._queue[SongQueue._currentSongIndex]
            song_url = song['url']

            await SongQueue.messageSongPlaying(song)
            SongQueue._currentSongIndex += 1

            if SongQueue._loop and SongQueue._currentSongIndex == len(SongQueue._queue):
                SongQueue._currentSongIndex = 0

            player = await YoutubeManager.GetYTLDSource(url=song_url)
            voice_channel.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(SongQueue.playSong(),
                                                                                        loop=SongQueue._ctx.bot.loop))

    @staticmethod
    async def skipSong():
        voice_channel = get(SongQueue._ctx.bot.voice_clients, guild=SongQueue._ctx.guild)
        if SongQueue._currentSongIndex >= len(SongQueue._queue) and SongQueue._loop:
            SongQueue._currentSongIndex = 0

        voice_channel.stop()
        await SongQueue.messageSongSkipped(SongQueue._queue[SongQueue._currentSongIndex - 1])

    @staticmethod
    async def pauseSong():
        voice_channel = get(SongQueue._ctx.bot.voice_clients, guild=SongQueue._ctx.guild)

        if not voice_channel.is_playing():
            await SongQueue.sendErrorMessage("No song currently playing")
            return

        voice_channel.pause()
        await SongQueue.messageSongPaused(SongQueue._queue[SongQueue._currentSongIndex - 1])

    @staticmethod
    async def resumeSong():
        voice_channel = get(SongQueue._ctx.bot.voice_clients, guild=SongQueue._ctx.guild)

        if not voice_channel.is_paused():
            await SongQueue.sendErrorMessage("No song currently paused")
            return

        voice_channel.resume()
        await SongQueue.messageSongResumed(SongQueue._queue[SongQueue._currentSongIndex - 1])

    @staticmethod
    async def loopQueue():
        server = SongQueue._ctx.message.guild
        voice_channel = server.voice_client

        SongQueue._loop = not SongQueue._loop
        await SongQueue.messageLoopQueueStatus()
        if SongQueue._currentSongIndex == len(SongQueue._queue) and not voice_channel.is_playing():
            SongQueue._currentSongIndex = 0
            await SongQueue.playSong()

    @staticmethod
    def clearQueue():
        SongQueue._queue.clear()
        SongQueue._loop = False
        SongQueue._currentSongIndex = 0
