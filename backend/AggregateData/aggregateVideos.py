import os

from django.db.models import Sum, F

from backend.AggregateData.lda import LDA
from backend.models import WordCountForLesson, WordCountForCourse, BinomioCountForCourse, BinomioCountForLesson, \
    Sentence


class AggregateVideos:

    def genereteTotalLda(self, corso):
        sentences = Sentence.objects.filter(lezione__corso=corso).order_by('number')

        tokenSentences = []
        for sentence in sentences:
            tokenSentences.append(sentence.sentence.split(' '))

        lda = LDA()
        lda.findTopicFromSenteces(tokenSentences, nTopic=4)
        lda.saveOnDBCorso(corso)
        return self

    def genereteCommonWords(self, corso):
        WordCountForCourse.objects.filter(corso=corso).delete()
        wordsAggregation = WordCountForLesson.objects.filter(lezione__corso=corso) \
            .values('lezione__corso', 'word').annotate(corso=F('lezione__corso'), count=Sum('count')) \
            .values('corso', 'word', 'count')
        for word in wordsAggregation:
            wordCountForCourse = WordCountForCourse(corso_id=word['corso'], word=word['word'], count=word['count'])
            wordCountForCourse.save()

    def genereteCommonBinomi(self, corso):
        BinomioCountForCourse.objects.filter(corso=corso).delete()
        binomiAggregation = BinomioCountForLesson.objects.filter(lezione__corso=corso) \
            .values('lezione__corso', 'binomio').annotate(corso=F('lezione__corso'), count=Sum('count')) \
            .values('corso', 'binomio', 'count')
        for binomio in binomiAggregation:
            binomioCountForCourse = BinomioCountForCourse(
                corso_id=binomio['corso'], binomio=binomio['binomio'], count=binomio['count'])
            binomioCountForCourse.save()

