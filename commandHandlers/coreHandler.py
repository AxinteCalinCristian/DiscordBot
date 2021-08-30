from commandHandlers.play import PlayCommand


class CoreHandler:
    @staticmethod
    async def handleCommand(cmd):
        if cmd.content.startswith('play'):
            bot_cmd = PlayCommand(cmd)
            await bot_cmd.handleCommand()
