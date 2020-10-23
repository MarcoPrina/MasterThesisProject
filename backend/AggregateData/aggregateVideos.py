import os

from django.db.models import Sum, F, Count, Q

from backend.AggregateData.lda import LDA
from backend.models import WordCountForLesson, WordCountForCourse, BinomioCountForCourse, BinomioCountForLesson, \
    Sentence, Corso


class AggregateVideos:

    def genereteTotalLda(self, corso):
        # Sentence.objects.filter(corso=corso).delete()  #TODO:scommentare, non mi serve ora per dei test
        sentences = Sentence.objects.filter(lezione__corso=corso).order_by('number')

        tokenSentences = []
        for sentence in sentences:
            tokenSentences.append(sentence.sentence.split(' '))

        lda = LDA()
        lda.findTopicFromSenteces(tokenSentences, nTopic=20)
        lda.saveOnDBCorso(corso)
        return self

    def genereteCommonWords(self, corso):
        WordCountForCourse.objects.filter(corso=corso).delete()
        wordsAggregation = WordCountForLesson.objects\
            .filter(lezione__corso=corso) \
            .values('lezione__corso', 'word') \
            .annotate(corso=F('lezione__corso'), count=Sum('count'), idf=Count('lezione', distinct=True)) \
            .values('corso', 'word', 'count', 'idf', 'id')
        tot_lesson = Corso.objects.filter(pk=corso.pk).annotate(tot_lesson=Count('lezione', distinct=True)).first().tot_lesson
        for word in wordsAggregation:
            idf = tot_lesson / word['idf']
            wordCountForCourse = WordCountForCourse(corso_id=word['corso'], word=word['word'], count=word['count'],
                                                    idf=idf)
            wordCountForCourse.save()
            wcfl = WordCountForLesson.objects.get(pk=word['id'])
            wcfl.tfidf = wcfl.tf * idf
            wcfl.save()

    def genereteCommonBinomi(self, corso):
        BinomioCountForCourse.objects.filter(corso=corso).delete()
        binomiAggregation = BinomioCountForLesson.objects.filter(lezione__corso=corso) \
            .values('lezione__corso', 'binomio').annotate(corso=F('lezione__corso'), count=Sum('count')) \
            .values('corso', 'binomio', 'count')
        for binomio in binomiAggregation:
            binomioCountForCourse = BinomioCountForCourse(
                corso_id=binomio['corso'], binomio=binomio['binomio'], count=binomio['count'])
            binomioCountForCourse.save()
