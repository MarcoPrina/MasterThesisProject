import json
import os
from collections import defaultdict

from backend.models import Words


class Prioritize():

    def __init__(self, tokenizedCaptions: []) -> None:
        self.tokenizedCaptions = tokenizedCaptions
        self.ordered = []

    def getOrdered(self, lezione, posTag=['']) -> list:
        words = {}
        totWords = 0
        for token in self.tokenizedCaptions:
            totWords += 1
            if token['pos'].startswith(tuple(posTag)):

                wor = Words(word=token['word'][:-1], time_stamp=token["time"], lezione=lezione)
                wor.save()

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

    def generateFile(self, directoryName: str, fileName='words'):
        if os.path.exists('Outputs/' + directoryName + "/" + fileName + ".csv"):
            os.remove('Outputs/' + directoryName + "/" + fileName + ".csv")
        wordsFile = open('Outputs/' + directoryName + "/" + fileName + ".csv", "a")

        wordsFile.write('word' + ";" + 'counter' + ";" + 'pos' + ";" + 'tf' + '\r\n')
        for word, data in self.ordered:
            orderedPOS = sorted(data['pos'].items(), key=lambda x: x[1], reverse=True)
            wordsFile.write(word + ";" + str(data['counter']) + ";" + orderedPOS[0][0] + ";" + str(data['tf']) + '\r\n')

        wordsFile.close()
