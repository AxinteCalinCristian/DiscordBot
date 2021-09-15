import discord
from discord.ext import commands, tasks
from discord.utils import get

from Commands import LeaveVoiceChannel, AddSongToQueue
from Utils import YoutubeManager, SongQueue, YoutubeSearch

client = commands.Bot(command_prefix='-')
YoutubeManager.setClient(client)
SongQueue.setClient(client)


# UTILS

def is_connected(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


async def sendNotInVoiceChannel(ctx):
    embed = discord.Embed(title='Not in a voice channel',
                          color=0x344245)

    await ctx.channel.send(embed=embed)

# EVENTS

@client.event
async def on_ready():
    print('Bot is online!')


@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if reaction.message.id == SongQueue.getCurrentQueueMessage().id:
        await SongQueue.displayQueueHandleReaction(reaction, user)


# COMMANDS

@client.command(name='play', help='Adds song to queue')
async def play(ctx, *args):
    q_string = ''
    for arg in args:
        q_string += arg + ' '
    q_string = q_string[:-1]

    await AddSongToQueue(ctx=ctx, q_string=q_string)


@client.command(name='queue', help='Displays the queue')
async def displayQueue(ctx, *args):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    if len(args) > 0 and args[0] == 'loop':
        SongQueue.setCtx(ctx)
        await SongQueue.loopQueue()
    else:
        SongQueue.setCtx(ctx)
        await SongQueue.displayQueue()


@client.command(name='loop', help='Toggles queue looping')
async def loopQueue(ctx, args):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    if args == 'queue':
        SongQueue.setCtx(ctx)
        await SongQueue.loopQueue()


@client.command(name='remove', help='Removes song at provided index from queue')
async def removeSong(ctx, index):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    SongQueue.setCtx(ctx)
    await SongQueue.deleteSong(index)


@client.command(name='skip', help='Skips current song')
async def skipSong(ctx, *args):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    SongQueue.setCtx(ctx)
    if len(args) > 0:
        await SongQueue.skipSongIndex(args[0])
    else:
        await SongQueue.skipSong()


@client.command(name='next', help='Skips current song')
async def skipSong(ctx):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    SongQueue.setCtx(ctx)
    await SongQueue.skipSong()


@client.command(name='pause', help='Pauses current song')
async def pauseSong(ctx):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    SongQueue.setCtx(ctx)
    await SongQueue.pauseSong()


@client.command(name='stop', help='Pauses current song')
async def pauseSong(ctx):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    SongQueue.setCtx(ctx)
    await SongQueue.pauseSong()


@client.command(name='resume', help='Resumes paused song')
async def resumeSong(ctx):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    SongQueue.setCtx(ctx)
    await SongQueue.resumeSong()


@client.command(name='leave', help='Makes bot leave the voice channel')
async def stop(ctx):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    await LeaveVoiceChannel(ctx)


class Core:
    _token = None
    _google_api_key = None

    def __init__(self, token, google_api_key):
        self._token = token
        self._google_api_key = google_api_key

    def runBot(self):
        YoutubeSearch.setApiKey(self._google_api_key)
        client.run(self._token)
