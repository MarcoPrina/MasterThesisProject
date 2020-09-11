import json
import logging
import os

from django.db import transaction
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import threading

from backend.AggregateData.parseVideo import ParseVideo

from django.core.files.storage import default_storage

from backend.AggregateData.tokenize import Tokenize
from backend.api.serializers import CorsoSerializer, LezioneSerializer, WordsSerializer, BinomiSerializer
from backend.models import Corsi, Lezioni, Words, Binomi


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


class CorsoDetails(APIView):

    def get(self, request, pk):
        corso = get_corso(pk)
        lezioni = Lezioni.objects.filter(corso=corso)
        serializer = LezioneSerializer(lezioni, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        corso = get_corso(pk)
        corso.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RetriveWords(APIView):

    def get(self, request):
        word = request.query_params.get('word')[:-1]
        corsoPk = request.query_params.get('corso')
        lezionePk = request.query_params.get('lezione')
        if not word:
            return Response('need word parameter', status=status.HTTP_400_BAD_REQUEST)
        if lezionePk:
            lezione = get_lezione(lezionePk)
            words = Words.objects.filter(word__icontains=word, lezione=lezione)
        elif corsoPk:
            corso = get_corso(corsoPk)
            words = Words.objects.filter(word__icontains=word, lezione__corso=corso)
        else:
            return Response('need lezione or corso parameter', status=status.HTTP_400_BAD_REQUEST)
        serializer = WordsSerializer(words, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Search(APIView):

    def get(self, request):
        query = request.query_params.get('query')
        corsoPk = request.query_params.get('corso')
        lezionePk = request.query_params.get('lezione')

        if not query:
            return Response('need query parameter', status=status.HTTP_400_BAD_REQUEST)

        tokens = Tokenize(query).getTokens()

        words = []

        for token in tokens:
            if token['pos'].startswith(tuple(['S', 'A'])): # TODO: serve veramente? oppure cerco direttamente se è contenuto?
                words.append(token['word'][:-1])

        if len(words) == 0:
            return Response('fornire una o due parole "nome nome" o "nome aggettivo"', status=status.HTTP_400_BAD_REQUEST)

        if len(words) == 1:
            if lezionePk:
                lezione = get_lezione(lezionePk)
                word = Words.objects.filter(word__iexact=words[0], lezione=lezione)
            elif corsoPk:
                corso = get_corso(corsoPk)
                word = Words.objects.filter(word__iexact=words[0], lezione__corso=corso)
            else:
                return Response('need lezione or corso parameter', status=status.HTTP_400_BAD_REQUEST)
            serializer = WordsSerializer(word, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif len(words) == 2:
            if lezionePk:
                lezione = get_lezione(lezionePk)
                binomi1 = Binomi.objects.filter(word1__icontains=words[0], word2__icontains=words[1], lezione=lezione)
                binomi2 = Binomi.objects.filter(word1__icontains=words[1], word2__icontains=words[0], lezione=lezione)
                binomi = binomi1.union(binomi2)
            elif corsoPk:
                corso = get_corso(corsoPk)
                binomi1 = Binomi.objects.filter(word1__icontains=words[0], word2__icontains=words[1], lezione__corso=corso)
                binomi2 = Binomi.objects.filter(word1__icontains=words[1], word2__icontains=words[0], lezione__corso=corso)
                binomi = binomi1.union(binomi2)
            else:
                return Response('need lezione or corso parameter', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('inserire una o due parole al massimo', status=status.HTTP_400_BAD_REQUEST)

        serializer = BinomiSerializer(binomi, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
            AnalyzeVideo(video_name, input_data,  serializer).start()

            return Response('Analyzing video', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnalyzeVideo(threading.Thread):
    logger = logging.getLogger(__name__)

    def __init__(self, video_path, input_data, serializer):
        threading.Thread.__init__(self)
        self.video_path = video_path
        self.input_data = input_data
        self.serializer = serializer

    def run(self):
        try:
            # TODO: separare quando crea i caption ( in cui non serve il db) da quando
            # elabora i dati, ottimizzare per avere più lezioni assieme

            parser = ParseVideo(self.input_data)\
                .getCaptionFromFile('/home/marco/PycharmProjects/AggregateData/Outputs/1/caption.txt')
            #    .getCaptionFromVideo(self.video_name, 'backend/YoutubeAPI/credentials.json')

            parser.parseFromCaption(posTag=['S', 'A'])
            # TODO: concentrare transaction e fare gestione errore
            with transaction.atomic():
                self.serializer.save()

                lezione = Lezioni.objects.get(pk=self.serializer.data['id'])

                parser.saveOnDB(lezione=lezione)

                lezione.processata = True
                lezione.save()

        except Exception as e:
            self.logger.error('Error analyzing video of "%s" corso in "%s" lesson',
                              self.serializer.data['corso'],
                              self.serializer.data['nome'],
                              exc_info=e)

        os.remove(self.video_path)
        # os.remove(self.video_name.replace("Video", "Audio", 1) + '.flac')


def get_corso(pk):
    try:
        return Corsi.objects.get(pk=pk)

    except Corsi.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


def get_lezione(pk):
    try:
        return Lezioni.objects.get(pk=pk)

    except Lezioni.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
