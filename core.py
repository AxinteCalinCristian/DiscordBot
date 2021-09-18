import discord
from discord.ext import commands
from discord.utils import get
import asyncio

from Commands import LeaveVoiceChannel, AddSongToQueue
from Utils import YoutubeManager, SongQueue, YoutubeSearch

client = commands.Bot(command_prefix='-')
YoutubeManager.setClient(client)
SongQueue.setClient(client)
leave_voice_channel = None


# UTILS

def is_connected(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


async def sendNotInVoiceChannel(ctx):
    embed = discord.Embed(title=f'**{client.user.display_name}** is not in a voice channel',
                          color=0x344245)

    await ctx.channel.send(embed=embed)


async def sendUserNotInVC(ctx):
    embed = discord.Embed(title=f'{ctx.author.display_name} please join a channel to issue commands',
                          color=0x344245)

    await ctx.channel.send(embed=embed)


async def sendNoCommandFoundError(ctx):
    embed = discord.Embed(title=f'No such command or incomplete command',
                          color=0x344245)

    await ctx.channel.send(embed=embed)


async def leaveVC(voice_channel):
    await asyncio.sleep(delay=20, loop=client.loop)
    await LeaveVoiceChannel(vc=voice_channel)


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


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await sendNoCommandFoundError(ctx)
    else:
        raise error


@client.event
async def on_voice_state_update(member, before, after):
    if not member.bot:
        global leave_voice_channel
        if after.channel is None:
            voice_channel = client.get_channel(before.channel.id)
            leave_voice_channel = asyncio.create_task(leaveVC(voice_channel))
            members = voice_channel.members
            if len(members) == 1 and members[0].id == client.user.id:
                await leave_voice_channel
        else:
            voice_channel = client.get_channel(after.channel.id)
            members = voice_channel.members

            if len(members) > 1:
                for member in members:
                    if client.user.id == member.id:
                        if leave_voice_channel is not None:
                            leave_voice_channel.cancel()
                            leave_voice_channel = None


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
    elif not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    elif len(args) > 0:
        if args[0] == 'loop':
            SongQueue.setCtx(ctx)
            SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
            await SongQueue.loopQueue()
        elif args[0] == 'clear':
            SongQueue.setCtx(ctx)
            SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
            SongQueue.clearQueue()
            await SongQueue.sendClearQueueMessage()
        else:
            await sendNoCommandFoundError(ctx)
    else:
        SongQueue.setCtx(ctx)
        SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
        await SongQueue.displayQueue()


@client.command(name='loop', help='Toggles queue looping')
async def loopQueue(ctx, *args):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    elif not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    if len(args) > 0:
        if args[0] == 'queue':
            SongQueue.setCtx(ctx)
            SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
            await SongQueue.loopQueue()
        else:
            await sendNoCommandFoundError(ctx)
    else:
        await sendNoCommandFoundError(ctx)


@client.command(name='clear', help='Clears queue')
async def clearQueue(ctx, *args):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    elif not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    if len(args) > 0:
        if args[0] == 'queue':
            SongQueue.setCtx(ctx)
            SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
            SongQueue.clearQueue()
            await SongQueue.sendClearQueueMessage()
        else:
            await sendNoCommandFoundError(ctx)


@client.command(name='remove', help='Removes song at provided index from queue')
async def removeSong(ctx, index):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    elif not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    SongQueue.setCtx(ctx)
    SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
    await SongQueue.deleteSong(index)


@client.command(name='skip', help='Skips current song')
async def skipSong(ctx, *args):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    elif not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    SongQueue.setCtx(ctx)
    SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
    if len(args) > 0:
        await SongQueue.skipSongIndex(args[0])
    else:
        await SongQueue.skipSong()


@client.command(name='next', help='Skips current song')
async def skipSong(ctx):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    elif not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    SongQueue.setCtx(ctx)
    SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
    await SongQueue.skipSong()


@client.command(name='pause', help='Pauses current song')
async def pauseSong(ctx):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    elif not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    SongQueue.setCtx(ctx)
    SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
    await SongQueue.pauseSong()


@client.command(name='stop', help='Pauses current song')
async def pauseSong(ctx):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    elif not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    SongQueue.setCtx(ctx)
    SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
    await SongQueue.pauseSong()


@client.command(name='resume', help='Resumes paused song')
async def resumeSong(ctx):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    elif not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    SongQueue.setCtx(ctx)
    SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
    await SongQueue.resumeSong()


@client.command(name='leave', help='Makes bot leave the voice channel')
async def stop(ctx):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    elif not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    await LeaveVoiceChannel(ctx=ctx)


class Core:
    _token = None
    _google_api_key = None

    def __init__(self, token, google_api_key):
        self._token = token
        self._google_api_key = google_api_key

    def runBot(self):
        YoutubeSearch.setApiKey(self._google_api_key)
        client.run(self._token)
