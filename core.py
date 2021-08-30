import discord
from commandHandlers.coreHandler import CoreHandler

client = discord.Client()


@client.event
async def on_ready():
    print('Bot ready')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('-'):
        message.content = message.content[1:]
        await CoreHandler.handleCommand(message)


class Core:
    def __init__(self, token):
        self._token = token

    def runBot(self):
        client.run(self._token)



