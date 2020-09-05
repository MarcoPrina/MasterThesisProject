import json
import os
from collections import defaultdict


class FindBinomi():

    def __init__(self, tokenizedCaptions: []) -> None:
        self.binomi = []
        self.tokenizedCaptions = tokenizedCaptions

    def searchForTwo(self, posTag=['']) -> json:
        self.binomi = []
        pre = {}
        first = True
        buffBinomi = {}
        totBinomi = 0
        for token in self.tokenizedCaptions:
            totBinomi += 1
            if not first and token['pos'].startswith(tuple(posTag)):
                binomio = pre['word'] + ' ' + token['word']
                lemmaBinomio = pre['word'][:-1] + ' ' + token['word'][:-1]
                if(lemmaBinomio in buffBinomi):
                    buffBinomi[lemmaBinomio]['count'] += 1
                else:
                    buffBinomi[lemmaBinomio] = {
                        'word':  binomio,
                        'pos':      pre['pos'] + ' ' + token['pos'],
                        'count': 1
                    }
                first = True
            elif first and token['pos'].startswith('S'):
                first = False
                pre = token

        for binomio in buffBinomi:
            buffBinomi[binomio]['tf'] = buffBinomi[binomio]['count']/totBinomi

        self.binomi = sorted(buffBinomi.items(), key=lambda x: x[1]['count'], reverse=True)
        return self.binomi

    def searchForThree(self, posTag=['']) -> json: #TODO: da riguardare, non va
        self.binomi = []
        pre0 = {}
        pre1 = {}
        first = True
        second = False
        buffBinomi = defaultdict(int)
        for sentence in self.tokenizedCaptions['sentences']:
            for token in sentence['tokens']:
                if first and token['pos'].startswith('S'):
                    first = False
                    second = True
                    pre0 = token
                elif second and token['pos'].startswith(tuple(posTag)):
                    second = False
                    pre1 = token
                elif token['pos'].startswith(tuple(posTag)):
                    buffBinomi[pre0['word'] + ';' + pre0['pos'] + ';' + pre1['word'] + ';' + pre1['pos'] + ';' + token['word'] + ';' + token['pos']] += 1
                    first = True
                    second = False
        self.binomi = sorted(buffBinomi.items(), key=lambda x: x[1], reverse=True)
        return self.binomi

    def generateFile(self, directoryName: str, fileName='binomi'):
        if os.path.exists('Outputs/' + directoryName + "/" + fileName + ".csv"):
            os.remove('Outputs/' + directoryName + "/" + fileName + ".csv")
        binomiFile = open('Outputs/' + directoryName + "/" + fileName + ".csv", "a")

        binomiFile.write(
            'binomio troncato' +
            ';' +
            'binomio' +
            ';' +
            'pos' +
            ';' +
            'count' +
            ';' +
            'tf' +
            '\r\n'
        )
        for binomio in self.binomi:
            binomiFile.write(
                binomio[0] +
                ';' +
                binomio[1]['word'] +
                ';' +
                binomio[1]['pos'] +
                ';' +
                str(binomio[1]['count']) +
                ';' +
                str(binomio[1]['tf']) +
                '\r\n'
            )


