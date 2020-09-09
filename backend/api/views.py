import json
import logging
import os

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import threading

from backend.AggregateData.parseVideo import ParseVideo

from django.core.files.storage import default_storage

from backend.api.serializers import CorsoSerializer, LezioneSerializer
from backend.models import Corsi, Lezioni


class CorsiAPIView(APIView):

    def get(self, request):
        corsi = Corsi.objects.all()
        serializer = CorsoSerializer(corsi, many=True)
        return Response(serializer.data)

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

        serializer = LezioneSerializer(data=input_data)
        if serializer.is_valid():
            AnalyzeVideo(video_name, serializer).start()

            return Response('Analyzing video', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnalyzeVideo(threading.Thread):
    logger = logging.getLogger(__name__)

    def __init__(self, video_name, serializer):
        threading.Thread.__init__(self)
        self.video_name = video_name
        self.serializer = serializer

    # @transaction.atomic()
    def run(self):
        try:
            with transaction.atomic():
                self.serializer.save()
                ParseVideo(self.serializer.data) \
                    .getCaptionFromFile('Outputs/prova/caption.txt') \
                    .parseFromCaption(posTag=['S', 'A'])
                #    .getCaptionFromVideo(self.video_name, 'backend/YoutubeAPI/credentials.json') \
                #    .parseFromCaption(posTag=['S', 'A'])

                lezione = Lezioni.objects.get(pk=self.serializer.data['id'])
                lezione.processata = True
                lezione.save()

        except Exception as e:
            self.logger.error('Error analyzing video of "%s" corso in "%s" lesson',
                              self.serializer.data['corso'],
                              self.serializer.data['nome'],
                              exc_info=e)

        os.remove(self.video_name)
        # os.remove(self.video_name.replace("Video", "Audio", 1) + '.flac')
