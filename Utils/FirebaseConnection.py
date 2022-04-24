import firebase_admin
from decouple import config
from firebase_admin import credentials, db, firestore


class FirebaseConnection:
    def __init__(self):
        self._cred = credentials.Certificate(config('FIREBASE_SERVICE_ACCOUNT_CRED'))
        self._app = firebase_admin.initialize_app(self._cred)
        self._db = firestore.client()

    def addPlaylist(self, name, disc_id, data, force=False):
        playlists = self._db.collection('playlists')
        check_exists = playlists.where('name', '==', name).where('discord_id', '==', disc_id).get()

        if not force and len(check_exists) > 0:
            return False, f'Playlist {name} already exists'

        song_urls, song_names = data
        to_add = {'name': name, 'discord_id': disc_id, 'song_urls': song_urls, 'song_names': song_names}
        if force and len(check_exists) > 0:
            playlists.document(check_exists[0].id).set(to_add)
            return True, f'Playlist {name} updated'

        playlists.add(to_add)
        return True, f'Playlist {name} added to database'

    def peekPlaylist(self, name, disc_id):
        playlists = self._db.collection('playlists')
        check_exists = playlists.where('name', '==', name).where('discord_id', '==', disc_id).get()

        if len(check_exists) == 0:
            return False, f'Playlist {name} doesn\'t exist'

        peek_data = check_exists[0].to_dict()

        data = []
        idx = 0
        while idx < len(peek_data['song_urls']):
            data.append({'name': peek_data['song_names'][idx], 'url': peek_data['song_urls'][idx]})
            idx += 1

        return True, data

    def getPlaylist(self, name, disc_id):
        playlists = self._db.collection('playlists')
        check_exists = playlists.where('name', '==', name).where('discord_id', '==', disc_id).get()

        if len(check_exists) == 0:
            return False, f'Playlist {name} doesn\'t exist'

        data = check_exists[0].to_dict()
        data = data['song_urls']
        return True, data

    def getPlaylists(self):
        playlists = self._db.collection('playlists').get()
        data = []
        for playlist in playlists:
            data.append({'name': playlist.to_dict()['name'], 'size': len(playlist.to_dict()['song_urls'])})
        return data
