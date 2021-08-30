import os
import discord
from decouple import config

client = discord.Client()
my_secret = config('TOKEN')


@client.event
async def on_ready():
    print('your god has arrived')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('-play'):
        song_name = 'placeholder'
        await message.channel.send(f'Now playing {song_name}')w

print(my_secret)
client.run(my_secret)
