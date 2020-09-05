import json

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import threading

from backend.AggregateData.parseVideo import ParseVideo


class thread(threading.Thread):
    def __init__(self, video):
        threading.Thread.__init__(self)
        self.video = video

        # helper function to execute the threads

    def run(self):
        ParseVideo('prova') \
            .getCaptionFromVideo(self.video) \
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
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            thread.start_new_thread(print_time, ("Thread-1", 2,))
            thread.start_new_thread(print_time, ("Thread-2", 4,))
        except:
            print
            "Error: unable to start thread"

        data = {'patata'}
        return Response(data, status=status.HTTP_201_CREATED)
