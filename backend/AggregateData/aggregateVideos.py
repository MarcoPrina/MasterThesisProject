import math
import os
import threading
import time

from django.db.models import Sum, F, Count, Q

from backend.AggregateData.lda import LDA
from backend.models import WordCountForLesson, WordCountForCourse, BinomioCountForCourse, BinomioCountForLesson, \
    Sentence, Corso, Lezione, LdaCorso


class AggregateVideos(threading.Thread):

    def __init__(self, corso):
        threading.Thread.__init__(self)
        self.corso = corso

    def run(self):
        self.genereteCommonBinomi()
        self.genereteCommonWords()
        self.genereteTotalLda()
        print('fine')

    def genereteTotalLda(self):
        LdaCorso.objects.filter(corso=self.corso).delete()
        tokenSentences = []

        '''

        sentences = Sentence.objects.filter(lezione__corso=self.corso).order_by('number')
        for sentence in sentences:
            tokenSentences.append(sentence.sentence.split(' '))

        '''
        lezioni = Lezione.objects.filter(corso=self.corso)
        for lezione in lezioni:
            sentences = Sentence.objects.filter(lezione=lezione).order_by('number')
            buff_sent = []
            for sentence in sentences:
                buff_sent = buff_sent + sentence.sentence.split(' ')
            tokenSentences.append(buff_sent)

        lda = LDA()
        lda.findTopicFromSenteces(tokenSentences, nTopic=14)
        lda.saveOnDBCorso(self.corso)
        return self

    def genereteCommonWords(self):
        WordCountForCourse.objects.filter(corso=self.corso).delete()

        wordsAggregation = WordCountForLesson.objects\
            .filter(lezione__corso=self.corso) \
            .values('lezione__corso', 'word') \
            .annotate(corso=F('lezione__corso'), count2=Sum('count'), idf=Count('lezione', distinct=True)) \
            .values('corso', 'word', 'count2', 'idf')
        tot_lesson = Corso.objects\
            .filter(pk=self.corso.pk)\
            .annotate(tot_lesson=Count('lezione', distinct=True))\
            .first().tot_lesson

        for word in wordsAggregation:
            idf = tot_lesson / word['idf']

            wordCountForCourse = WordCountForCourse(
                corso_id=word['corso'], word=word['word'], count=word['count2'], idf=idf)
            wordCountForCourse.save()

            wcfls = WordCountForLesson.objects.filter(word=word['word'], lezione__corso=self.corso)
            for wcfl in wcfls:
                wcfl.tfidf = wcfl.tf * idf
                wcfl.save()

    def genereteCommonBinomi(self):
        BinomioCountForCourse.objects.filter(corso=self.corso).delete()

        binomiAggregation = BinomioCountForLesson.objects\
            .filter(lezione__corso=self.corso) \
            .values('lezione__corso', 'binomio')\
            .annotate(corso=F('lezione__corso'), count=Sum('count'), idf=Count('lezione', distinct=True)) \
            .values('corso', 'binomio', 'count', 'idf')

        tot_lesson = Corso.objects\
            .filter(pk=self.corso.pk)\
            .annotate(tot_lesson=Count('lezione', distinct=True))\
            .first().tot_lesson

        for binomio in binomiAggregation:
            idf = math.log(tot_lesson / binomio['idf'])
            binomioCountForCourse = BinomioCountForCourse(
                corso_id=binomio['corso'], binomio=binomio['binomio'], count=binomio['count'], idf=idf)
            binomioCountForCourse.save()

            bcfls = BinomioCountForLesson.objects.filter(binomio=binomio['binomio'], lezione__corso=self.corso)
            for bcfl in bcfls:
                bcfl.tfidf = bcfl.tf * idf
                bcfl.save()
