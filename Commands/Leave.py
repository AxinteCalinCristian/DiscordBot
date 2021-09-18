import discord

from Utils.SongQueue import SongQueue


async def NotifyUser(ctx, msg):
    embed = discord.Embed(title=msg,
                          color=0x870c4c)
    embed.set_author(name='Bot kicked',
                     icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


async def LeaveVoiceChannel(ctx=None, vc=None):
    if ctx is not None:
        await NotifyUser(ctx, 'Leaving the voice channel')
        voice_client = ctx.message.guild.voice_client
        SongQueue.setVoiceChannelID(ctx.author.voice.channel.id)
    else:
        SongQueue.setVoiceChannelID(vc.id)
        voice_client = vc.members[0].guild.voice_client

    if SongQueue.getCurrentQueueMessage() is not None:
        await SongQueue.getCurrentQueueMessage().clear_reactions()
        SongQueue.setCurrentQueueMessage(None)

    await voice_client.disconnect()
    SongQueue.clearQueue()
