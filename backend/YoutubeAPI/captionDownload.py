import io
import os

import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaIoBaseDownload

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]


class CaptionDownload():

    def __init__(self, credentials) -> None:
        self.credentials = credentials

    def get(self, videoID, directoryName: str, output_file='caption.vtt'):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # TODO: eliminare in prod

        api_service_name = "youtube"
        api_version = "v3"

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=self.credentials)

        requestCaptionID = youtube.captions().list(
            part="id",
            videoId=videoID
        )
        response = requestCaptionID.execute()
        captionID = response['items'][0]['id']

        request = youtube.captions().download(
            id=captionID,
            tfmt="vtt"
        )

        fh = io.FileIO('Outputs/' + directoryName + '/' + output_file, "wb")

        download = MediaIoBaseDownload(fh, request)
        complete = False
        while not complete:
            status, complete = download.next_chunk()
