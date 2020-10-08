import math
import os
from pathlib import Path

from django.db.models import Sum, F

from backend.AggregateData.lda import LDA
from backend.models import WordCountForLesson, WordCountForCourse, BinomioCountForCourse, BinomioCountForLesson


class AggregateVideos():

    def genereteTotalTokens(self):
        lessons = os.listdir('Outputs')

        if os.path.exists('Outputs/totalVideo/totalToken.csv'):
            os.remove('Outputs/totalVideo/totalToken.csv')
        totalToken = open('Outputs/totalVideo/totalToken.csv', 'a')

        for lesson in lessons:
            if self.isALesson(lesson):
                with open('Outputs/' + lesson + '/token.csv') as f:
                    next(f)
                    tokens = [line.rstrip() for line in f]
                    for token in tokens:
                        totalToken.write(token + ';' + lesson + '\r\n')
        return self

    def genereteTotalLda(self):
        sentencesWithToken = []
        with open('Outputs/totalVideo/totalToken.csv') as f:
            next(f)
            token = [line.strip().split(';') for line in f]
            for data in token:
                sentencesWithToken.append({
                    'word': data[0],
                    'time': data[1],
                    'pos': data[2],
                })

        lda = LDA()
        lda.findTopic(sentencesWithToken, posTag=['S', 'A'], nTopic=4)
        lda.saveOnDB()
        return self

    def genereteCommonWords(self, lezione):
        WordCountForCourse.objects.filter(corso_id=lezione.corso).delete()
        wordsAggregation = WordCountForLesson.objects.filter(lezione__corso=lezione.corso) \
            .values('lezione__corso', 'word').annotate(corso=F('lezione__corso'), count=Sum('count')) \
            .values('corso', 'word', 'count')
        for word in wordsAggregation:
            wordCountForCourse = WordCountForCourse(corso_id=word['corso'], word=word['word'], count=word['count'])
            wordCountForCourse.save()

    def genereteCommonBinomi(self, lezione):
        BinomioCountForCourse.objects.filter(corso_id=lezione.corso).delete()
        binomiAggregation = BinomioCountForLesson.objects.filter(lezione__corso=lezione.corso) \
            .values('lezione__corso', 'binomio').annotate(corso=F('lezione__corso'), count=Sum('count')) \
            .values('corso', 'binomio', 'count')
        for binomio in binomiAggregation:
            binomioCountForCourse = BinomioCountForCourse(
                corso_id=binomio['corso'], binomio=binomio['binomio'], count=binomio['count'])
            binomioCountForCourse.save()

