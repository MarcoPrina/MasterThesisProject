import json
import os
from collections import defaultdict

from backend.models import Word, WordCount


class FindWords():

    def __init__(self) -> None:
        self.ordered = []
        self.words = []

    def search(self, tokenizedCaptions, posTag=['']) -> list:
        words = {}
        totWords = 0
        for token in tokenizedCaptions:
            totWords += 1
            if token['pos'].startswith(tuple(posTag)):

                self.words.append({
                    'word': token['word'][:-1],
                    'time_stamp': token['time']
                })

                if token['word'] in words:
                    words[token['word']]['counter'] += 1
                    words[token['word']]['pos'][token['pos']] += 1
                else:
                    words[token['word']] = {}
                    words[token['word']]['counter'] = 1
                    words[token['word']]['word'] = token['word']
                    words[token['word']]['pos'] = defaultdict(int)
                    words[token['word']]['pos'][token['pos']] += 1

        for word in words:
            words[word]['tf'] = words[word]['counter'] / totWords
        self.ordered = sorted(words.items(), key=lambda x: x[1]['counter'], reverse=True)
        return self.ordered

    def saveOnDB(self, lezione):

        for word in self.words:
            wor = Word(word=word['word'], time_stamp=word["time_stamp"], lezione=lezione)
            wor.save()

        for word, data in self.ordered:
            wor = WordCount(word=word, count=data['counter'], lezione=lezione, tf=data['tf'])
            wor.save()
