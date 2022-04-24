import discord
from discord.utils import get
import re

from Utils import YoutubeSearch, SongQueue, YoutubeManager


def is_connected(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


async def NotifyUser(ctx, msg):
    embed = discord.Embed(title=msg,
                          color=0x344245)

    await ctx.channel.send(embed=embed)


def isUrl(q_string):
    regex = '^(?:https?:\/\/)?(?:www\.)?((youtube.com\/watch\?v=)|(youtu.be\/))[^\s]+$'

    if re.search(regex, q_string):
        return True
    else:
        return False


def isPlaylist(q_string):
    regex = '^(?:https?:\/\/)?(?:www\.)?youtube.com\/playlist[^\s]+$'

    if re.search(regex, q_string):
        return True
    else:
        return False


async def getUrlFromQueryString(q_string):
    url = await YoutubeSearch.getUrl(q_string)
    return url


async def AddSongToQueue(ctx, q_string):
    if not ctx.message.author.voice:
        await NotifyUser(ctx, "You are not connected to a voice channel")
        return

    channel = ctx.message.author.voice.channel
    if not is_connected(ctx):
        await channel.connect()
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)

    is_playlist = False
    if isUrl(q_string):
        url = q_string
    elif isPlaylist(q_string):
        url = q_string
        is_playlist = True
    else:
        url = await getUrlFromQueryString(q_string)

    if url != '':
        if not is_playlist:
            player = await YoutubeManager.GetYTLDSource(url=url)

            song = {'name': player.getSongName(), 'url': url, 'requester': ctx.message.author,
                    'duration': player.getSongDuration()}

            SongQueue.setCtx(ctx)
            SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
            await SongQueue.addSong(song=song)
        else:
            player = await YoutubeManager.GetYTLDSource(url=url)
            songs = player.getPlaylistSongs()

            for song in songs:
                song['requester'] = ctx.message.author

            playlist = {'name': player.getPlaylistName(), 'url': player.getPlaylistUrl(), 'songs': songs}

            SongQueue.setCtx(ctx)
            SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
            await SongQueue.addPlaylist(playlist)
    else:
        await NotifyUser(ctx, 'No songs found')


async def LoadPlaylist(ctx, urls):
    if not ctx.message.author.voice:
        await NotifyUser(ctx, "You are not connected to a voice channel")
        return []

    channel = ctx.message.author.voice.channel
    if not is_connected(ctx):
        await channel.connect()
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)

    song_list = []

    for url in urls:
        player = await YoutubeManager.GetYTLDSource(url=url)

        song = {'name': player.getSongName(), 'url': url, 'requester': ctx.message.author,
                'duration': player.getSongDuration()}

        song_list.append(song)

    return song_list
