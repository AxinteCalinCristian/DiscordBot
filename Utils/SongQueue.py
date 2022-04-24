import asyncio
import discord
from emoji import EMOJI_ALIAS_UNICODE_ENGLISH as EMOJIS

from discord.utils import get
from Utils.YoutubeManager import YoutubeManager


class SongQueue:
    _queue = {}
    _loop = {}
    _ctx = None
    _client = None
    _currentSongIndex = {}
    _queueDisplayMessage = {}
    _queuePageNumber = {}
    _vc_id = None
    _peek_queue = {}
    _peek_queueDisplayMessage = {}
    _peek_queuePageNumber = {}
    _peek_queue_names = {}
    # MESSAGES

    @staticmethod
    async def messageSongPlaying(song):
        embed = discord.Embed(title=song['name'], url=song['url'],
                              color=0x63b7f2)
        embed.set_author(name='Now playing',
                         icon_url=SongQueue._ctx.author.avatar_url)
        embed.add_field(name="Duration", value=str(song['duration']), inline=True)
        embed.add_field(name="Position in queue", value=str(SongQueue._currentSongIndex[SongQueue._vc_id] + 1) + '/' +
                                                        str(len(SongQueue._queue[SongQueue._vc_id])), inline=True)
        await SongQueue._ctx.channel.send(embed=embed)

    @staticmethod
    async def messageSongAdded(song):
        embed = discord.Embed(title=song['name'], url=song['url'],
                              color=0x18b549)
        embed.set_author(name='Added to queue',
                         icon_url=SongQueue._ctx.author.avatar_url)
        embed.add_field(name="Duration", value=str(song['duration']), inline=True)
        embed.add_field(name="Position in queue", value=str(len(SongQueue._queue[SongQueue._vc_id])) + '/' +
                                                        str(len(SongQueue._queue[SongQueue._vc_id])), inline=True)
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

        if SongQueue._currentSongIndex[SongQueue._vc_id] == 0 and len(SongQueue._queue[SongQueue._vc_id]) == 1:
            carry = 1
        else:
            carry = 0

        embed.add_field(name="Position in queue",
                        value=str(SongQueue._currentSongIndex[SongQueue._vc_id] + carry) + '/' +
                              str(len(SongQueue._queue[SongQueue._vc_id])), inline=True)
        await SongQueue._ctx.channel.send(embed=embed)

    @staticmethod
    async def messageSongResumed(song):
        embed = discord.Embed(title=song['name'], url=song['url'],
                              color=0x920bd6)
        embed.set_author(name='Song resumed',
                         icon_url=SongQueue._ctx.author.avatar_url)
        embed.add_field(name="Duration", value=str(song['duration']), inline=True)

        if SongQueue._currentSongIndex[SongQueue._vc_id] == 0 and len(SongQueue._queue[SongQueue._vc_id]) == 1:
            carry = 1
        else:
            carry = 0

        embed.add_field(name="Position in queue",
                        value=str(SongQueue._currentSongIndex[SongQueue._vc_id] + carry) + '/' +
                              str(len(SongQueue._queue[SongQueue._vc_id])), inline=True)
        await SongQueue._ctx.channel.send(embed=embed)

    @staticmethod
    async def messageSongSkipped(song):
        embed = discord.Embed(title=song['name'], url=song['url'],
                              color=0xf74514)
        embed.set_author(name='Song skipped',
                         icon_url=SongQueue._ctx.author.avatar_url)
        embed.add_field(name="Duration", value=str(song['duration']), inline=True)

        if SongQueue._currentSongIndex[SongQueue._vc_id] == 0:
            carry = 1
        else:
            carry = 0

        embed.add_field(name="Position in queue",
                        value=str(SongQueue._currentSongIndex[SongQueue._vc_id] + carry) + '/' +
                              str(len(SongQueue._queue[SongQueue._vc_id])), inline=True)
        await SongQueue._ctx.channel.send(embed=embed)

    @staticmethod
    async def messageLoopQueueStatus():
        if SongQueue._loop[SongQueue._vc_id]:
            embed = discord.Embed(title="Now looping the queue",
                                  color=0xbcd40d)
            await SongQueue._ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(title="Stopped looping the queue",
                                  color=0xbcd40d)
            await SongQueue._ctx.channel.send(embed=embed)

    @staticmethod
    async def displayQueue():
        if SongQueue._queueDisplayMessage[SongQueue._vc_id] is not None:
            await SongQueue._queueDisplayMessage[SongQueue._vc_id].clear_reactions()

        if len(SongQueue._queue[SongQueue._vc_id]) == 0:
            await SongQueue.sendErrorMessage('Queue is empty')
            return

        embed = discord.Embed(title=f'Queue for {SongQueue._ctx.message.guild.name}',
                              color=0xed34e4)

        SongQueue._queuePageNumber[SongQueue._vc_id] = 0
        content = ''

        server = SongQueue._ctx.message.guild
        voice_channel = server.voice_client
        if voice_channel.is_playing() or voice_channel.is_paused():
            if SongQueue._currentSongIndex[SongQueue._vc_id] == 0:
                carry = 1
            else:
                carry = 0

            current_song = SongQueue._queue[SongQueue._vc_id][SongQueue._currentSongIndex[SongQueue._vc_id] - 1]
            content += f"**Now playing**: `{SongQueue._currentSongIndex[SongQueue._vc_id] + carry}.` [{current_song['name']}]({current_song['url']})\n\n"

        idx = 0
        while idx < min(len(SongQueue._queue[SongQueue._vc_id]), 10):
            song = SongQueue._queue[SongQueue._vc_id][idx]
            song_name = song['name']
            song_url = song['url']
            requester = song['requester']
            duration = song['duration']

            content += f"`{idx + 1}.` [{song_name}]({song_url})  |  `{duration}`\n`Requested by {requester}\n`"
            if idx < len(SongQueue._queue[SongQueue._vc_id]):
                content += '\n'

            idx += 1

        embed.description = content
        if SongQueue._loop[SongQueue._vc_id]:
            status_emoji = EMOJIS[':white_check_mark:']
        else:
            status_emoji = EMOJIS[':x:']
        embed.set_footer(
            text=f'Page: {SongQueue._queuePageNumber[SongQueue._vc_id] + 1}/{(-(-len(SongQueue._queue[SongQueue._vc_id]) // 10))} | Loop queue: {status_emoji}')

        msg = await SongQueue._ctx.channel.send(embed=embed)
        await msg.add_reaction(EMOJIS[':black_left__pointing_double_triangle_with_vertical_bar:'])
        await msg.add_reaction(EMOJIS[':black_right__pointing_double_triangle_with_vertical_bar:'])
        SongQueue._queueDisplayMessage[SongQueue._vc_id] = msg

    @staticmethod
    async def peekQueue():
        if SongQueue._peek_queueDisplayMessage[SongQueue._vc_id] is not None:
            await SongQueue._peek_queueDisplayMessage[SongQueue._vc_id].clear_reactions()

        if len(SongQueue._peek_queue[SongQueue._vc_id]) == 0:
            await SongQueue.sendErrorMessage('Queue is empty')
            return

        embed = discord.Embed(title=f'Peeking queue {SongQueue._peek_queue_names[SongQueue._vc_id]}',
                              color=0xed34e4)

        SongQueue._queuePageNumber[SongQueue._vc_id] = 0
        content = ''

        idx = 0
        while idx < min(len(SongQueue._peek_queue[SongQueue._vc_id]), 10):
            song = SongQueue._peek_queue[SongQueue._vc_id][idx]
            song_name = song['name']
            song_url = song['url']
            content += f"`{idx + 1}.` [{song_name}]({song_url})"

            if idx < len(SongQueue._peek_queue[SongQueue._vc_id]):
                content += '\n'

            idx += 1

        embed.description = content
        embed.set_footer(
            text=f'Page: {SongQueue._peek_queuePageNumber[SongQueue._vc_id] + 1}/{(-(-len(SongQueue._peek_queue[SongQueue._vc_id]) // 10))}')

        msg = await SongQueue._ctx.channel.send(embed=embed)
        await msg.add_reaction(EMOJIS[':black_left__pointing_double_triangle_with_vertical_bar:'])
        await msg.add_reaction(EMOJIS[':black_right__pointing_double_triangle_with_vertical_bar:'])
        SongQueue._peek_queueDisplayMessage[SongQueue._vc_id] = msg

    @staticmethod
    async def loadPlaylist(playlist):
        SongQueue.clearQueue()
        server = SongQueue._ctx.message.guild
        voice_channel = server.voice_client
        for song in playlist:
            if not voice_channel.is_playing() and not voice_channel.is_paused():
                SongQueue._queue[SongQueue._vc_id].append(song)
                await SongQueue.playSong()
            else:
                SongQueue._queue[SongQueue._vc_id].append(song)
                if SongQueue._currentSongIndex[SongQueue._vc_id] == 0:
                    SongQueue._currentSongIndex[SongQueue._vc_id] = len(SongQueue._queue[SongQueue._vc_id]) - 1
        await SongQueue.skipSongIndex('1', False)

    @staticmethod
    async def appendPlaylist(playlist):
        server = SongQueue._ctx.message.guild
        voice_channel = server.voice_client
        for song in playlist:
            if not voice_channel.is_playing() and not voice_channel.is_paused():
                SongQueue._queue[SongQueue._vc_id].append(song)
                await SongQueue.playSong()
            else:
                SongQueue._queue[SongQueue._vc_id].append(song)
                if SongQueue._currentSongIndex[SongQueue._vc_id] == 0:
                    SongQueue._currentSongIndex[SongQueue._vc_id] = len(SongQueue._queue[SongQueue._vc_id]) - 1

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

    @staticmethod
    async def sendClearQueueMessage():
        embed = discord.Embed(title='Song queue cleared',
                              color=0x7104b5)

        await SongQueue._ctx.channel.send(embed=embed)

    # ACTIONS

    @staticmethod
    def setCtx(ctx):
        SongQueue._ctx = ctx

    @staticmethod
    def getCtx():
        return SongQueue._ctx

    @staticmethod
    def setVoiceChannelID(vc_id):
        SongQueue._vc_id = str(vc_id)
        if not (SongQueue._vc_id in SongQueue._queue.keys()):
            SongQueue._queue[SongQueue._vc_id] = []
        if not (SongQueue._vc_id in SongQueue._loop.keys()):
            SongQueue._loop[SongQueue._vc_id] = True
        if not (SongQueue._vc_id in SongQueue._currentSongIndex.keys()):
            SongQueue._currentSongIndex[SongQueue._vc_id] = 0
        if not (SongQueue._vc_id in SongQueue._queueDisplayMessage.keys()):
            SongQueue._queueDisplayMessage[SongQueue._vc_id] = None
        if not (SongQueue._vc_id in SongQueue._queuePageNumber.keys()):
            SongQueue._queuePageNumber[SongQueue._vc_id] = 0
        if not (SongQueue._vc_id in SongQueue._peek_queue.keys()):
            SongQueue._peek_queue[SongQueue._vc_id] = []
        if not (SongQueue._vc_id in SongQueue._peek_queueDisplayMessage.keys()):
            SongQueue._peek_queueDisplayMessage[SongQueue._vc_id] = None
        if not (SongQueue._vc_id in SongQueue._peek_queuePageNumber.keys()):
            SongQueue._peek_queuePageNumber[SongQueue._vc_id] = 0

    @staticmethod
    def setPeekQueue(data, name):
        SongQueue._peek_queue[SongQueue._vc_id] = data
        SongQueue._peek_queue_names[SongQueue._vc_id] = name

    @staticmethod
    def getVoiceChannelID():
        return SongQueue._vc_id

    @staticmethod
    def setClient(client):
        SongQueue._client = client

    @staticmethod
    def getCurrentQueueMessage():
        return SongQueue._queueDisplayMessage[SongQueue._vc_id]

    @staticmethod
    def getCurrentPeekQueueMessage():
        return SongQueue._peek_queueDisplayMessage[SongQueue._vc_id]

    @staticmethod
    def setCurrentQueueMessage(value):
        SongQueue._queueDisplayMessage[SongQueue._vc_id] = value

    @staticmethod
    def setCurrentPeekQueueMessage(value):
        SongQueue._peek_queueDisplayMessage[SongQueue._vc_id] = value

    @staticmethod
    async def addSong(song):
        for q_song in SongQueue._queue[SongQueue._vc_id]:
            if q_song['url'] == song['url']:
                await SongQueue.sendErrorMessage('Song already in queue')
                return
        server = SongQueue._ctx.message.guild
        voice_channel = server.voice_client
        if not voice_channel.is_playing() and not voice_channel.is_paused():
            SongQueue._queue[SongQueue._vc_id].append(song)
            await SongQueue.messageSongAdded(song)
            await SongQueue.playSong()
        else:
            SongQueue._queue[SongQueue._vc_id].append(song)
            if SongQueue._currentSongIndex[SongQueue._vc_id] == 0:
                SongQueue._currentSongIndex[SongQueue._vc_id] = len(SongQueue._queue[SongQueue._vc_id]) - 1
            await SongQueue.messageSongAdded(song)

    @staticmethod
    async def addPlaylist(playlist):
        for song in playlist['songs']:
            SongQueue._queue[SongQueue._vc_id].append(song)

        await SongQueue.addedPlaylistToQueue(playlist)

        server = SongQueue._ctx.message.guild
        voice_channel = server.voice_client
        if not voice_channel.is_playing():
            await SongQueue.playSong()

    @staticmethod
    async def deleteSong(index):
        if not index.isnumeric():
            if index == 'all':
                SongQueue.clearQueue()
                await SongQueue.sendClearQueueMessage()
                voice_channel = get(SongQueue._ctx.bot.voice_clients, guild=SongQueue._ctx.guild)
                if voice_channel.is_playing() or voice_channel.is_paused() :
                    voice_channel.stop()
                return
            await SongQueue.sendErrorMessage("Please provide a valid index")
            return
        elif index.isnumeric() and int(index) < 1 or int(index) > len(SongQueue._queue[SongQueue._vc_id]):
            await SongQueue.sendErrorMessage("Please provide a valid index")
            return

        index = int(index) - 1
        await SongQueue.messageSongRemoved(SongQueue._queue[SongQueue._vc_id][index])
        voice_channel = get(SongQueue._ctx.bot.voice_clients, guild=SongQueue._ctx.guild)

        if SongQueue._currentSongIndex[SongQueue._vc_id] >= index:
            SongQueue._currentSongIndex[SongQueue._vc_id] -= 1

        if voice_channel.is_playing() and SongQueue._currentSongIndex[SongQueue._vc_id] == index:
            voice_channel.stop()

        del SongQueue._queue[SongQueue._vc_id][index]

    @staticmethod
    async def playSong():
        if SongQueue._currentSongIndex[SongQueue._vc_id] < len(SongQueue._queue[SongQueue._vc_id]):
            voice_channel = get(SongQueue._ctx.bot.voice_clients, guild=SongQueue._ctx.guild)
            song = SongQueue._queue[SongQueue._vc_id][SongQueue._currentSongIndex[SongQueue._vc_id]]
            song_url = song['url']

            if voice_channel.is_connected():
                await SongQueue.messageSongPlaying(song)
            SongQueue._currentSongIndex[SongQueue._vc_id] += 1

            if SongQueue._loop[SongQueue._vc_id] and SongQueue._currentSongIndex[SongQueue._vc_id] == len(
                    SongQueue._queue[SongQueue._vc_id]):
                SongQueue._currentSongIndex[SongQueue._vc_id] = 0

            player = await YoutubeManager.GetYTLDSource(url=song_url)
            voice_channel.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(SongQueue.playSong(),
                                                                                        loop=SongQueue._ctx.bot.loop))

    @staticmethod
    async def skipSongIndex(index, info=True):
        if not index.isnumeric():
            if info:
                await SongQueue.sendErrorMessage("Enter a number")
            return

        index = int(index) - 1
        if index < 0 or index >= len(SongQueue._queue[SongQueue._vc_id]):
            if info:
                await SongQueue.sendErrorMessage("Enter a valid index")
            return
        if info:
            await SongQueue.messageSongSkipped(
                SongQueue._queue[SongQueue._vc_id][SongQueue._currentSongIndex[SongQueue._vc_id] - 1])
        SongQueue._currentSongIndex[SongQueue._vc_id] = index
        voice_channel = get(SongQueue._ctx.bot.voice_clients, guild=SongQueue._ctx.guild)
        voice_channel.stop()

    @staticmethod
    async def skipSong():
        if len(SongQueue._queue[SongQueue._vc_id]) == 0:
            await SongQueue.sendErrorMessage("Queue is empty")
            return

        if len(SongQueue._queue[SongQueue._vc_id]) == 1 and SongQueue._currentSongIndex[SongQueue._vc_id] == 1 and not \
        SongQueue._loop[SongQueue._vc_id]:
            voice_channel = get(SongQueue._ctx.bot.voice_clients, guild=SongQueue._ctx.guild)

            if voice_channel.is_playing():
                await SongQueue.messageSongSkipped(SongQueue._queue[SongQueue._vc_id][0])
                voice_channel.stop()
            else:
                await SongQueue.sendErrorMessage("No song to skip")

            return

        if len(SongQueue._queue[SongQueue._vc_id]) == 1 and SongQueue._loop[SongQueue._vc_id]:
            voice_channel = get(SongQueue._ctx.bot.voice_clients, guild=SongQueue._ctx.guild)
            SongQueue._currentSongIndex[SongQueue._vc_id] = 0
            voice_channel.stop()
            await SongQueue.messageSongSkipped(SongQueue._queue[SongQueue._vc_id][0])

            return

        voice_channel = get(SongQueue._ctx.bot.voice_clients, guild=SongQueue._ctx.guild)
        await SongQueue.messageSongSkipped(
            SongQueue._queue[SongQueue._vc_id][SongQueue._currentSongIndex[SongQueue._vc_id] - 1])

        voice_channel.stop()

        if SongQueue._currentSongIndex[SongQueue._vc_id] >= len(SongQueue._queue[SongQueue._vc_id]) and SongQueue._loop[
            SongQueue._vc_id]:
            SongQueue._currentSongIndex[SongQueue._vc_id] = 0

    @staticmethod
    async def pauseSong():
        voice_channel = get(SongQueue._ctx.bot.voice_clients, guild=SongQueue._ctx.guild)

        if not voice_channel.is_playing():
            await SongQueue.sendErrorMessage("No song currently playing")
            return

        voice_channel.pause()
        await SongQueue.messageSongPaused(
            SongQueue._queue[SongQueue._vc_id][SongQueue._currentSongIndex[SongQueue._vc_id] - 1])

    @staticmethod
    async def resumeSong():
        voice_channel = get(SongQueue._ctx.bot.voice_clients, guild=SongQueue._ctx.guild)

        if not voice_channel.is_paused():
            await SongQueue.sendErrorMessage("No song currently paused")
            return

        voice_channel.resume()
        await SongQueue.messageSongResumed(
            SongQueue._queue[SongQueue._vc_id][SongQueue._currentSongIndex[SongQueue._vc_id] - 1])

    @staticmethod
    async def loopQueue():
        server = SongQueue._ctx.message.guild
        voice_channel = server.voice_client

        SongQueue._loop[SongQueue._vc_id] = not SongQueue._loop[SongQueue._vc_id]
        await SongQueue.messageLoopQueueStatus()
        if SongQueue._currentSongIndex[SongQueue._vc_id] == len(SongQueue._queue[SongQueue._vc_id]):
            SongQueue._currentSongIndex[SongQueue._vc_id] = 0
            if not voice_channel.is_playing():
                await SongQueue.playSong()

    @staticmethod
    def getQueue():
        urls = []
        names = []
        for song in SongQueue._queue[SongQueue._vc_id]:
            urls.append(song['url'])
            names.append(song['name'])
        return urls, names

    @staticmethod
    def clearQueue():
        SongQueue._queue[SongQueue._vc_id].clear()
        SongQueue._loop[SongQueue._vc_id] = True
        SongQueue._currentSongIndex[SongQueue._vc_id] = 0

    @staticmethod
    async def displayQueueHandleReaction(reaction, user):

        change_page = False

        if reaction.emoji == EMOJIS[':black_left__pointing_double_triangle_with_vertical_bar:']:

            if SongQueue._queuePageNumber[SongQueue._vc_id] > 0:
                change_page = True
                SongQueue._queuePageNumber[SongQueue._vc_id] -= 1

        elif reaction.emoji == EMOJIS[':black_right__pointing_double_triangle_with_vertical_bar:']:

            if SongQueue._queuePageNumber[SongQueue._vc_id] < (-(-len(SongQueue._queue[SongQueue._vc_id]) // 10)) - 1:
                change_page = True
                SongQueue._queuePageNumber[SongQueue._vc_id] += 1

        if change_page:
            embed = discord.Embed(title=f'Queue for {SongQueue._ctx.message.guild.name}',
                                  color=0xed34e4)
            content = ''

            server = SongQueue._ctx.message.guild
            voice_channel = server.voice_client
            if voice_channel.is_playing() or voice_channel.is_paused():
                if SongQueue._currentSongIndex[SongQueue._vc_id] == 0:
                    carry = 1
                else:
                    carry = 0

                current_song = SongQueue._queue[SongQueue._vc_id][SongQueue._currentSongIndex[SongQueue._vc_id] - 1]
                content += f"**Now playing**: `{SongQueue._currentSongIndex[SongQueue._vc_id] + carry}.` [{current_song['name']}]({current_song['url']})\n\n"

            idx = 10 * SongQueue._queuePageNumber[SongQueue._vc_id]
            while idx < min(10 * (SongQueue._queuePageNumber[SongQueue._vc_id] + 1),
                            len(SongQueue._queue[SongQueue._vc_id])):
                song = SongQueue._queue[SongQueue._vc_id][idx]
                song_name = song['name']
                song_url = song['url']
                requester = song['requester']
                duration = song['duration']

                content += f"`{idx + 1}.` [{song_name}]({song_url})  |  `{duration}`\n`Requested by {requester}\n`"
                if idx < len(SongQueue._queue[SongQueue._vc_id]):
                    content += '\n'

                idx += 1

            embed.description = content
            if SongQueue._loop[SongQueue._vc_id]:
                status_emoji = EMOJIS[':white_check_mark:']
            else:
                status_emoji = EMOJIS[':x:']
            embed.set_footer(
                text=f'Page: {SongQueue._queuePageNumber[SongQueue._vc_id] + 1}/{(-(-len(SongQueue._queue[SongQueue._vc_id]) // 10))} | Loop queue: {status_emoji}')

            await SongQueue._queueDisplayMessage[SongQueue._vc_id].edit(embed=embed)

        await reaction.remove(user)

    @staticmethod
    async def displayPeekQueueHandleReaction(reaction, user):

        change_page = False

        if reaction.emoji == EMOJIS[':black_left__pointing_double_triangle_with_vertical_bar:']:

            if SongQueue._peek_queuePageNumber[SongQueue._vc_id] > 0:
                change_page = True
                SongQueue._peek_queuePageNumber[SongQueue._vc_id] -= 1

        elif reaction.emoji == EMOJIS[':black_right__pointing_double_triangle_with_vertical_bar:']:

            if SongQueue._peek_queuePageNumber[SongQueue._vc_id] < (-(-len(SongQueue._peek_queue[SongQueue._vc_id]) // 10)) - 1:
                change_page = True
                SongQueue._peek_queuePageNumber[SongQueue._vc_id] += 1

        if change_page:
            embed = discord.Embed(title=f'Peeking queue {SongQueue._peek_queue_names[SongQueue._vc_id]}',
                                  color=0xed34e4)
            content = ''

            idx = 10 * SongQueue._peek_queuePageNumber[SongQueue._vc_id]
            while idx < min(10 * (SongQueue._peek_queuePageNumber[SongQueue._vc_id] + 1),
                            len(SongQueue._peek_queue[SongQueue._vc_id])):
                song = SongQueue._peek_queue[SongQueue._vc_id][idx]
                song_name = song['name']
                song_url = song['url']
                content += f"`{idx + 1}.` [{song_name}]({song_url})"
                if idx < len(SongQueue._peek_queue[SongQueue._vc_id]):
                    content += '\n'

                idx += 1

            embed.description = content

            embed.set_footer(
                text=f'Page: {SongQueue._peek_queuePageNumber[SongQueue._vc_id] + 1}/{(-(-len(SongQueue._peek_queue[SongQueue._vc_id]) // 10))}')

            await SongQueue._peek_queueDisplayMessage[SongQueue._vc_id].edit(embed=embed)

        await reaction.remove(user)
