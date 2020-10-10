import json
import os
import re
import subprocess
import time

import requests
from tqdm import tqdm

from backend.models import Sentence


class Tokenize():

    def __init__(self) -> None:
        self.tokenizedCaptions = {}
        self.usableCaption = ''

    def getTokens(self, usableCaption: str) -> json:
        self.usableCaption = usableCaption.replace('\r\n', '\r').replace('\n', '\r')
        self.startTint()
        file = self.usableCaption.split('\r')
        tokenized = []
        with tqdm(total=len(file)) as pbar:
            for line in file:
                pbar.update(1)
                if line:
                    sentence = self.posLine(line)["sentences"][0]
                    remainingLine = line
                    time = ''
                    for token in sentence["tokens"]:
                        word = token['originalText']
                        lineParts = remainingLine.split(word, 1)
                        if len(lineParts) > 1 and lineParts[1]:
                            remainingLine = remainingLine.split(word, 1)[1].strip()
                            if '<' in remainingLine:
                                time = remainingLine[remainingLine.find('<')+1:].split('>', 1)[0]
                        token['time'] = time
                        tokenized.append(token)

        self.tokenizedCaptions = tokenized
        return tokenized


    def posLine(self, line) -> json:
        parsedLine = self.parseLine(line)
        parameters = {"text": parsedLine}
        response = requests.get("http://localhost:8012/tint", params=parameters)
        return response.json()

    def parseLine(self, line) -> str:
        parsedLine = line.replace("\\n", "").replace("\\r", "")
        return re.sub(r"<([^<>]*)>", "", parsedLine)

    def startTint(self):
        try:
            parameters = {"text": 'test'}
            response = requests.get("http://localhost:8012/tint", params=parameters)
        except:
            subprocess.Popen(["./tint/tint-server.sh", "-c", "./tint/sampleProps.properties"])
            time.sleep(7)

    def saveOnDB(self, lezione, posTag):
        buffSentence = ''
        number = 0
        for num, token in enumerate(self.tokenizedCaptions):
            if token['pos'].startswith(tuple(posTag)) and len(token['word']) > 2:
                buffSentence += ' ' + token['word'][:-1]
            if buffSentence and ('.' in token['word'] or '?' in token['word'] or '!' in token['word']):
                sentence = Sentence(lezione=lezione, sentence=buffSentence, number=number)
                sentence.save()
                number += 1
                buffSentence = ''

        if buffSentence:
            sentence = Sentence(lezione=lezione, sentence=buffSentence, number=number)
            sentence.save()



