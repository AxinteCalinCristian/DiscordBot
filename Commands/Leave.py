import discord

from Utils.SongQueue import SongQueue


async def NotifyUser(ctx, msg):
    embed = discord.Embed(title=msg,
                          color=0x870c4c)
    embed.set_author(name='Bot kicked',
                     icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


async def LeaveVoiceChannel(ctx):
    await NotifyUser(ctx, 'Leaving the voice channel')
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()
    await SongQueue.getCurrentQueueMessage().clear_reactions()
    SongQueue.setCurrentQueueMessage(None)
    SongQueue.clearQueue()
