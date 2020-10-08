import json
import os
from collections import defaultdict

from backend.models import Binomio, BinomioCountForLesson


class FindBinomi():

    def __init__(self) -> None:
        self.binomi = []
        self.countBinomi = []

    def searchForTwo(self, tokenizedCaptions, posTag=['']) -> json:
        self.binomi = []
        pre = {}
        first = True
        buffBinomi = {}
        totBinomi = 0
        for token in tokenizedCaptions:
            totBinomi += 1
            if not first and token['pos'].startswith(tuple(posTag)):
                binomio = pre['word'] + ' ' + token['word']
                lemmaBinomio = pre['word'][:-1] + ' ' + token['word'][:-1]

                self.binomi.append({
                    'word1': pre['word'][:-1],
                    'word2': token['word'][:-1],
                    'time_stamp': pre['time']
                })

                if (lemmaBinomio in buffBinomi):
                    buffBinomi[lemmaBinomio]['count'] += 1
                else:
                    buffBinomi[lemmaBinomio] = {
                        'word': binomio,
                        'pos': pre['pos'] + ' ' + token['pos'],
                        'count': 1
                    }
                first = True
            elif first and token['pos'].startswith('S'):
                first = False
                pre = token

        for binomio in buffBinomi:
            buffBinomi[binomio]['tf'] = buffBinomi[binomio]['count'] / totBinomi

        self.countBinomi = sorted(buffBinomi.items(), key=lambda x: x[1]['count'], reverse=True)
        return self

    def saveOnDB(self, lezione):
        for binomio in self.binomi:
            bin = Binomio(
                word1=binomio['word1'],
                word2=binomio['word2'],
                lezione=lezione,
                time_stamp=binomio['time_stamp']
            )
            bin.save()

        for binomio in self.countBinomi:
            bin = BinomioCountForLesson(
                binomio=binomio[1]['word'],
                lezione=lezione,
                count=binomio[1]['count'],
                tf=binomio[1]['tf'],
            )
            bin.save()
