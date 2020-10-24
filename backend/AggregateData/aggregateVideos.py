import os
import threading
import time

from django.db.models import Sum, F, Count, Q

from backend.AggregateData.lda import LDA
from backend.models import WordCountForLesson, WordCountForCourse, BinomioCountForCourse, BinomioCountForLesson, \
    Sentence, Corso


class AggregateVideos(threading.Thread):

    def __init__(self, corso):
        threading.Thread.__init__(self)
        self.corso = corso

    def run(self):
        self.genereteCommonBinomi()
        self.genereteCommonWords()
        self.genereteTotalLda()

    def genereteTotalLda(self):
        # Sentence.objects.filter(corso=corso).delete()  #TODO:scommentare, non mi serve ora per dei test
        sentences = Sentence.objects.filter(lezione__corso=self.corso).order_by('number')

        tokenSentences = []
        for sentence in sentences:
            tokenSentences.append(sentence.sentence.split(' '))

        lda = LDA()
        lda.findTopicFromSenteces(tokenSentences, nTopic=18)
        lda.saveOnDBCorso(self.corso)
        return self

    def genereteCommonWords(self):
        WordCountForCourse.objects.filter(corso=self.corso).delete()

        wordsAggregation = WordCountForLesson.objects\
            .filter(lezione__corso=self.corso) \
            .values('lezione__corso', 'word') \
            .annotate(corso=F('lezione__corso'), count=Sum('count'), idf=Count('lezione', distinct=True)) \
            .values('corso', 'word', 'count', 'idf', 'id')

        tot_lesson = Corso.objects\
            .filter(pk=self.corso.pk)\
            .annotate(tot_lesson=Count('lezione', distinct=True))\
            .first().tot_lesson

        for word in wordsAggregation:
            idf = tot_lesson / word['idf']

            wordCountForCourse = WordCountForCourse(
                corso_id=word['corso'], word=word['word'], count=word['count'], idf=idf)
            wordCountForCourse.save()

            wcfl = WordCountForLesson.objects.get(pk=word['id'])
            wcfl.tfidf = wcfl.tf * idf
            wcfl.save()

    def genereteCommonBinomi(self):
        BinomioCountForCourse.objects.filter(corso=self.corso).delete()

        binomiAggregation = BinomioCountForLesson.objects\
            .filter(lezione__corso=self.corso) \
            .values('lezione__corso', 'binomio')\
            .annotate(corso=F('lezione__corso'), count=Sum('count'), idf=Count('lezione', distinct=True)) \
            .values('corso', 'binomio', 'count', 'idf', 'id')

        tot_lesson = Corso.objects\
            .filter(pk=self.corso.pk)\
            .annotate(tot_lesson=Count('lezione', distinct=True))\
            .first().tot_lesson

        for binomio in binomiAggregation:
            idf = tot_lesson / binomio['idf']
            binomioCountForCourse = BinomioCountForCourse(
                corso_id=binomio['corso'], binomio=binomio['binomio'], count=binomio['count'], idf=idf)
            binomioCountForCourse.save()

            bcfl = BinomioCountForLesson.objects.get(pk=binomio['id'])
            bcfl.tfidf = bcfl.tf * idf
            bcfl.save()
