import os

import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


class PlaylistData():

    def __init__(self, credentials) -> None:
        self.credentials = credentials
        self.playlist = []

    def get(self, playlistID):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # TODO: eliminare in prod

        api_service_name = "youtube"
        api_version = "v3"

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=self.credentials)

        request = youtube.playlistItems().list(
            part="snippet",
            maxResults=50,
            playlistId=playlistID
        )
        playlistResponse = request.execute()

        for video in playlistResponse['items']:
            self.playlist.append({'title': video['snippet']['title'], 'videoId': video['snippet']['resourceId']['videoId']})
        return self

    def askLessons(self):
        print('\r\r')
        print('Sono state trovate ' + str(len(self.playlist)) + ' videolezioni.')
        print('Per ognuna inserire il numero della lezione partendo da 1 e premere invio')
        input("Premere invio per continuare")
        print('\r')
        for video in self.playlist:
            lesson = None
            while not lesson:
                print('Titolo video: ', video['title'])
                print('id video: ', video['videoId'])
                try:
                    lesson = int(input("Numero della lazione: "))
                except:
                    print('\r')
                    print("\x1b[31mInserire numero lezione\x1b[0m")
                print('\r')
            video['lesson'] = lesson

        self.playlist = sorted(self.playlist, key=lambda x: x['lesson'], reverse=False)
        return self
