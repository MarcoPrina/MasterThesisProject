import requests


class VimeoDownload:

    def __init__(self, credentialsPath) -> None:
        with open(credentialsPath) as f:
            self.credentials = f.read().strip()

    def get(self, videoID):
        get_video_link = requests.get('https://api.vimeo.com/me/videos/' + str(videoID),
                                      headers={
                                          'Authorization': 'Bearer ' + self.credentials
                                      })
        video_links = get_video_link.json()['download']

        size = 0
        link = ''
        for video_link in video_links:
            if size == 0 or video_link['size'] < size:
                size = video_link['size']
                link = video_link['link']

        with requests.get(link, stream=True) as r:
            with open('Media/Video/' + str(videoID,) + '.mp4', 'wb') as f:
                for chunk in r.iter_content(chunk_size=16*1024):
                    f.write(chunk)
