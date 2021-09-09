from googleapiclient.discovery import build


class YoutubeSearch:
    _google_api_key = None

    @staticmethod
    def setApiKey(api_key):
        YoutubeSearch._google_api_key = api_key

    @staticmethod
    def get_service():
        return build("youtube", "v3", developerKey=YoutubeSearch._google_api_key)

    @staticmethod
    def search(term):
        service = YoutubeSearch.get_service()
        response = service.search().list(
            part="id,snippet",
            q=term,
            maxResults=10
        ).execute()

        url = 'https://www.youtube.com/watch?v='

        videos = []

        for search_result in response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                videos.append(search_result['id']['videoId'])

        url += videos[0]
        return url

    @staticmethod
    async def getUrl(q_string):
        return YoutubeSearch.search(q_string)
