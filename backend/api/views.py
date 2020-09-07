import json

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import threading

from backend.AggregateData.parseVideo import ParseVideo

from django.core.files.storage import default_storage


class AnalyzeVideo(threading.Thread):
    def __init__(self, video_name):
        threading.Thread.__init__(self)
        self.video_name = video_name

        # helper function to execute the threads

    def run(self):
        print('potato')
        ParseVideo('prova') \
            .getCaptionFromVideo(self.video_name, 'backend/YoutubeAPI/credentials.json') \
            .parseFromCaption(posTag=['S', 'A'])  # TODO: togliere nome prova


class UploadVideo(APIView):

    @transaction.atomic()
    def post(self, request):
        input_data = {}
        try:
            input_data = json.loads(request.data['data'])
        except (KeyError, Exception):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            video = request.FILES['video']
            input_data.update({'video': video})
            video_name = default_storage.save('Media/Video/' + video.name, video)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        AnalyzeVideo(video_name).start()

        data = {'patata'}
        return Response(data, status=status.HTTP_201_CREATED)
