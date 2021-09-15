import youtube_dl

from Utils.YTDLSource import YTDLSource

youtube_dl.utils.bug_reports_message = lambda: ''

class YoutubeManager:
    _ytdl_format_options = {
                            'format': 'bestaudio/best',
                            'outtmpl': './AudioFiles/%(extractor)s-%(id)s-%(title)s.%(ext)s',
                            'restrictfilenames': True,
                            'noplaylist': True,
                            'nocheckcertificate': True,
                            'ignoreerrors': False,
                            'logtostderr': False,
                            'quiet': True,
                            'no_warnings': True,
                            'default_search': 'auto',
                            'source_address': '0.0.0.0'
                           }
    _ffmpeg_options = {
                        'options': '-vn',
                        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
                      }
    _ytld = youtube_dl.YoutubeDL(_ytdl_format_options)
    _client = None
    _YTLDSource = None

    @staticmethod
    def setClient(client):
        YoutubeManager._client = client

    @staticmethod
    async def GetYTLDSource(url):
        YoutubeManager._YTLDSource = await YTDLSource.fromUrl(url=url, ytld=YoutubeManager._ytld,
                                                              ffmpeg_options=YoutubeManager._ffmpeg_options,
                                                              loop=YoutubeManager._client.loop, stream=True)
        return YoutubeManager._YTLDSource

    @staticmethod
    def getSongName():
        return YoutubeManager._YTLDSource.getSongName()

    @staticmethod
    def getSongUrl():
        return YoutubeManager._YTLDSource.getSongUrl()
