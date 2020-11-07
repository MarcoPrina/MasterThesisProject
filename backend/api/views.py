from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api.serializers import CorsoSerializer, LezioneSerializer, WordListSerializer, BinomiListSerializer
from backend.models import Corso, Lezione, Word, Binomio


class CorsiAPIView(APIView):

    def get(self, request):
        nome = request.query_params.get('nome')
        if nome:
            corso = Corso.objects.get(nome__iexact=nome)
            serializer = CorsoSerializer(corso)
        else:
            corsi = Corso.objects.all()
            serializer = CorsoSerializer(corsi, many=True)
        return Response(serializer.data)


class HintView(APIView):

    def get(self, request):
        hint = request.query_params.get('hint')
        corsi = Corso.objects.filter(nome__icontains=hint)
        serializer = CorsoSerializer(corsi, many=True)
        return Response(serializer.data)


class CorsoDetails(APIView):

    def get(self, request, pk):
        try:
            corso = Corso.objects.get(pk=pk)

        except Corso.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        lezioni = Lezione.objects.filter(corso=corso).order_by("id")
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
            try:
                lezione = Lezione.objects.get(pk=lezionePk)

            except Lezione.DoesNotExist:
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)

            words = Word.objects.filter(word__icontains=word, lezione=lezione)
        elif corsoPk:
            try:
                corso = Corso.objects.get(pk=corsoPk)

            except Corso.DoesNotExist:
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)

            words = Word.objects.filter(word__icontains=word, lezione__corso=corso)
        else:
            return Response('need lezione or corso parameter', status=status.HTTP_400_BAD_REQUEST)
        serializer = WordListSerializer(words, many=True)
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
                try:
                    lezione = Lezione.objects.get(pk=lezionePk)

                except Lezione.DoesNotExist:
                    return HttpResponse(status=status.HTTP_404_NOT_FOUND)

                word = Word.objects.filter(word__icontains=words[0], lezione=lezione).distinct('word')
            elif corsoPk:
                try:
                    corso = Corso.objects.get(pk=corsoPk)

                except Corso.DoesNotExist:
                    return HttpResponse(status=status.HTTP_404_NOT_FOUND)

                word = Word.objects.filter(word__icontains=words[0], lezione__corso=corso).distinct('word')
            else:
                return Response('need lezione or corso parameter', status=status.HTTP_400_BAD_REQUEST)
            serializer = WordListSerializer(word, context={'corso': corsoPk, 'lezione': lezionePk}, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif len(words) == 2:
            if lezionePk:
                try:
                    lezione = Lezione.objects.get(pk=lezionePk)

                except Lezione.DoesNotExist:
                    return HttpResponse(status=status.HTTP_404_NOT_FOUND)

                binomi1 = Binomio.objects.filter(word1__icontains=words[0], word2__icontains=words[1], lezione=lezione) \
                    .distinct('word1', 'word2')
                binomi2 = Binomio.objects.filter(word1__icontains=words[1], word2__icontains=words[0], lezione=lezione) \
                    .distinct('word1', 'word2')
                binomi = binomi1.union(binomi2)
            elif corsoPk:
                try:
                    corso = Corso.objects.get(pk=corsoPk)

                except Corso.DoesNotExist:
                    return HttpResponse(status=status.HTTP_404_NOT_FOUND)

                binomi1 = Binomio.objects.filter(word1__icontains=words[0], word2__icontains=words[1],
                                                 lezione__corso=corso).distinct('word1', 'word2')
                binomi2 = Binomio.objects.filter(word1__icontains=words[1], word2__icontains=words[0],
                                                 lezione__corso=corso).distinct('word1', 'word2')
                binomi = binomi1.union(binomi2)

            else:
                return Response('need lezione or corso parameter', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('inserire una o due parole al massimo', status=status.HTTP_400_BAD_REQUEST)

        serializer = BinomiListSerializer(binomi, context={'corso': corsoPk, 'lezione': lezionePk}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
