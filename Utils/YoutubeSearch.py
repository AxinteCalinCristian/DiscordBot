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
    async def search(term):
        no_of_results = 10
        service = YoutubeSearch.get_service()
        response = service.search().list(
            part="id,snippet",
            q=term,
            safeSearch='strict',
            maxResults=no_of_results
        ).execute()

        url = 'https://www.youtube.com/watch?v='

        videos = []

        for search_result in response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                videos.append(search_result['id']['videoId'])

        if len(videos):
            url += videos[0]
        else:
            url = ''

        return url

    @staticmethod
    async def getUrl(q_string):
        url = await YoutubeSearch.search(q_string)
        return url