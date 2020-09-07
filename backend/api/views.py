import json
import os

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import threading

from backend.AggregateData.parseVideo import ParseVideo

from django.core.files.storage import default_storage

from backend.api.serializers import CorsoSerializer, LezioneSerializer
from backend.models import Corsi


class NewCorso(APIView):

    def post(self, request):
        serializer = CorsoSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewLezione(APIView):

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

        serializer = LezioneSerializer(data=input_data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            data['message'] = 'Analyzing video'
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnalyzeVideo(threading.Thread):
    def __init__(self, video_name):
        threading.Thread.__init__(self)
        self.video_name = video_name

    def run(self):
        print('potato')
        # try:
        ParseVideo('prova') \
            .getCaptionFromFile('Outputs/prova/caption.txt')\
            .parseFromCaption(posTag=['S', 'A'])
        #    .getCaptionFromVideo(self.video_name, 'backend/YoutubeAPI/credentials.json') \
        #    .parseFromCaption(posTag=['S', 'A'])  # TODO: togliere nome prova
        os.remove(self.video_name)
        # os.remove(self.video_name.replace("Video", "Audio", 1) + '.flac')
        # segnare video come "elaborato"
        # except Exception:
