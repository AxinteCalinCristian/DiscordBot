

class PlayCommand:

    def __init__(self, cmd):
        self._cmd = cmd

    def getQueryString(self):
        q_string = self._cmd.content

        index = 5
        while q_string[index] == ' ':
            index += 1

        res_str = q_string[index:]
        return res_str

    async def notifyUsers(self, song_name):
        await self._cmd.channel.send(f'Now playing {song_name}')

    async def handleCommand(self):
        querystring = self.getQueryString()
        # search for querystring
        song_name = 'placeholder'
        # playsong
        await self.notifyUsers(song_name)
