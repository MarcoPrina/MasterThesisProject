import json
import logging
import os
import re

from django.db import transaction
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import threading

from backend.AggregateData.parseVideo import ParseVideo

from django.core.files.storage import default_storage

from backend.api.serializers import CorsoSerializer, LezioneSerializer, WordsSerializer, BinomiSerializer
from backend.models import Corsi, Lezioni, Words, Binomi


class CorsiAPIView(APIView):

    def get(self, request):
        corsi = Corsi.objects.all()
        serializer = CorsoSerializer(corsi, many=True)
        return Response(serializer.data)


class CorsoDetails(APIView):

    def get(self, request, pk):
        corso = get_corso(pk)
        lezioni = Lezioni.objects.filter(corso=corso)
        serializer = LezioneSerializer(lezioni, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

        words = [word[:-1] for word in query.split(' ')]

        ''' tokens = Tokenize(query).getTokens()
        for token in tokens:
            if True or token['pos'].startswith(
                    tuple(['S', 'A'])):  # TODO: serve veramente? oppure cerco direttamente se è contenuto?
                words.append(token['word'][:-1])'''

        if len(words) == 0:
            return Response('fornire una o due parole "nome nome" o "nome aggettivo"',
                            status=status.HTTP_400_BAD_REQUEST)

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
                binomi1 = Binomi.objects.filter(word1__icontains=words[0], word2__icontains=words[1],
                                                lezione__corso=corso)
                binomi2 = Binomi.objects.filter(word1__icontains=words[1], word2__icontains=words[0],
                                                lezione__corso=corso)
                binomi = binomi1.union(binomi2)
            else:
                return Response('need lezione or corso parameter', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('inserire una o due parole al massimo', status=status.HTTP_400_BAD_REQUEST)

        serializer = BinomiSerializer(binomi, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
