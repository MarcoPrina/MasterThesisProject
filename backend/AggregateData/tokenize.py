import json
import os
import re
import subprocess

from tqdm import tqdm

import time

import requests


class Tokenize():

    def __init__(self, usableCaption: str) -> None:
        self.sentencesWithToken = {}
        self.usableCaption = usableCaption.replace('\r\n', '\r').replace('\n', '\r')

    def getTokens(self) -> json:
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
                        if token['time'] == '01:10:52.800':
                            print(token['time'])
                        tokenized.append(token)

        self.sentencesWithToken = tokenized
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

    def generateFile(self, directoryName: str, fileName='token'):
        if os.path.exists('Outputs/' + directoryName + "/" + fileName +".csv"):
            os.remove('Outputs/' + directoryName + "/" + fileName +".csv")
        tokenFile = open('Outputs/' + directoryName + "/" + fileName +".csv", "a")
        for token in self.sentencesWithToken:
            tokenFile.write(token['word'] + ';' + token['time'] + ';' + token['pos'] + '\r\n')
        tokenFile.close()



