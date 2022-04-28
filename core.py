import discord
from discord.ext import commands
from discord.utils import get
from Utils.FirebaseConnection import FirebaseConnection

from Commands import LeaveVoiceChannel, AddSongToQueue, LoadPlaylist
from Utils import YoutubeManager, SongQueue, YoutubeSearch

client = commands.Bot(command_prefix='-')
YoutubeManager.setClient(client)
SongQueue.setClient(client)
leave_voice_channel = None
firebase = FirebaseConnection()


# UTILS

cmds = {
    'save as <name>': 'Saves playlist to database',
    'overwrite <name>': 'Overwrites playlist in database',
    'peek <name>': 'Peeks playlist contents',
    'load <name>': 'Loads playlist contents',
    'append <name>': 'Loads playlist contents',
    'playlists': 'Displays all the playlists',
    'play <query / url>': 'Adds song to queue',
    'queue': 'Displays the queue',
    'loop queue / queue loop': 'Toggles queue looping',
    'clear': 'Clears queue',
    'remove <idx>': 'Removes song at provided index from queue',
    'skip <idx?>': 'Skips current song or skips to provided index',
    'next': 'Skips current song',
    'pause': 'Pauses current song',
    'stop': 'Stops current song',
    'leave': 'Makes bot leave the voice channel'
}


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


async def sendPlaylistError(ctx, resp):
    embed = discord.Embed(title=resp,
                          color=0xf74514)

    await ctx.channel.send(embed=embed)


async def sendPlaylistSaved(ctx, resp):
    embed = discord.Embed(title=resp,
                          color=0x18b549)

    await ctx.channel.send(embed=embed)


async def sendPlaylists(ctx, resp):
    embed = discord.Embed(title=f'Listing playlists for {ctx.message.guild.name}',
                          color=0x63b7f2)
    content = ''
    if len(resp) == 0:
        content = 'No saved playlists'
    else:
        for idx, pl in enumerate(resp):
            content += f'`{idx + 1}.` **' + pl['name'] + '**' + f" ({pl['size']} songs)"
            if idx < len(resp) - 1:
                content += '\n'

    embed.description = content
    await ctx.channel.send(embed=embed)


async def printCommands(ctx):
    embed = discord.Embed(title=f'All available commands',
                          color=0x63b7f2)
    content = ''
    if len(cmds) == 0:
        content = 'No saved playlists'
    else:
        for idx, cmd in enumerate(cmds.keys()):
            content += f'`{idx + 1}.` **' + cmd + '**\n' + f"> {cmds[cmd]}"
            if idx < len(cmds) - 1:
                content += '\n'

    embed.description = content
    await ctx.channel.send(embed=embed)


# EVENTS

@client.event
async def on_ready():
    print('Bot is online!')


@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if SongQueue.getCurrentQueueMessage() is not None and reaction.message.id == SongQueue.getCurrentQueueMessage().id:
        await SongQueue.displayQueueHandleReaction(reaction, user)
    elif SongQueue.getCurrentPeekQueueMessage() is not None and reaction.message.id == SongQueue.getCurrentPeekQueueMessage().id:
        await SongQueue.displayPeekQueueHandleReaction(reaction, user)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await sendNoCommandFoundError(ctx)
    else:
        raise error


# COMMANDS

@client.command(name='commands', help='Displays all the commands')
async def commands(ctx, *args):
    if len(args) > 0:
        await sendNoCommandFoundError(ctx)

    if not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    channel = ctx.message.author.voice.channel
    if not is_connected(ctx):
        await channel.connect()
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)

    await printCommands(ctx)


@client.command(name='save', help='Saves playlist to database')
async def save_playlist(ctx, *args):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    elif not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    if len(args) > 1:
        SongQueue.setCtx(ctx)
        SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
        if args[0] != 'as':
            await sendNoCommandFoundError(ctx)
            return
        status, resp = firebase.addPlaylist(name=args[1], disc_id=SongQueue.getVoiceChannelID(), data=SongQueue.getQueue())
        if not status:
            await sendPlaylistError(ctx, resp)
        else:
            await sendPlaylistSaved(ctx, resp)
    else:
        await sendNoCommandFoundError(ctx)


@client.command(name='overwrite', help='Overwrites playlist in database')
async def overwrite_playlist(ctx, *args):
    if not is_connected(ctx):
        await sendNotInVoiceChannel(ctx)
        return
    elif not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    if len(args) > 0:
        SongQueue.setCtx(ctx)
        SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
        status, resp = firebase.addPlaylist(name=args[0], disc_id=SongQueue.getVoiceChannelID(), data=SongQueue.getQueue(), force=True)
        if not status:
            await sendPlaylistError(ctx, resp)
        else:
            await sendPlaylistSaved(ctx, resp)
    else:
        await sendNoCommandFoundError(ctx)


@client.command(name='peek', help='Peeks playlist contents')
async def peek_playlist(ctx, *args):
    if not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    channel = ctx.message.author.voice.channel
    if not is_connected(ctx):
        await channel.connect()
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)
    if len(args) > 0:
        SongQueue.setCtx(ctx)
        SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
        status, resp = firebase.peekPlaylist(name=args[0], disc_id=SongQueue.getVoiceChannelID())
        if not status:
            await sendPlaylistError(ctx, resp)
        else:
            SongQueue.setPeekQueue(resp, args[0])
            await SongQueue.peekQueue()
    else:
        await sendNoCommandFoundError(ctx)


@client.command(name='load', help='Loads playlist contents')
async def load_playlist(ctx, *args):
    if not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    channel = ctx.message.author.voice.channel
    if not is_connected(ctx):
        await channel.connect()
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)
    if len(args) > 0:
        SongQueue.setCtx(ctx)
        SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
        status, resp = firebase.getPlaylist(name=args[0], disc_id=SongQueue.getVoiceChannelID())
        if not status:
            await sendPlaylistError(ctx, resp)
        else:
            songs = await LoadPlaylist(ctx, resp)
            await SongQueue.loadPlaylist(songs)
    else:
        await sendNoCommandFoundError(ctx)


@client.command(name='append', help='Loads playlist contents')
async def append_playlist(ctx, *args):
    if not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    channel = ctx.message.author.voice.channel
    if not is_connected(ctx):
        await channel.connect()
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)
    if len(args) > 0:
        SongQueue.setCtx(ctx)
        SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
        status, resp = firebase.getPlaylist(name=args[0], disc_id=SongQueue.getVoiceChannelID())
        if not status:
            await sendPlaylistError(ctx, resp)
        else:
            songs = await LoadPlaylist(ctx, resp)
            await SongQueue.appendPlaylist(songs)
    else:
        await sendNoCommandFoundError(ctx)


@client.command(name='playlists', help='Displays all the playlists')
async def playlists(ctx, *args):
    if len(args) > 0:
        await sendNoCommandFoundError(ctx)

    if not ctx.author.voice:
        await sendUserNotInVC(ctx)
        return
    channel = ctx.message.author.voice.channel
    if not is_connected(ctx):
        await channel.connect()
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)

    SongQueue.setCtx(ctx)
    SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)

    resp = firebase.getPlaylists(SongQueue.getVoiceChannelID())
    await sendPlaylists(ctx, resp)


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
