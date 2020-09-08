import os
import string, random
from pathlib import Path

from backend.AggregateData.breakAnalyzer import BreakAnalyzer
from backend.AggregateData.cropCaption import CropCaption
from backend.AggregateData.findBinomi import FindBinomi
from backend.AggregateData.lda import LDA
from backend.AggregateData.prioritize import Prioritize
from backend.AggregateData.tokenize import Tokenize
from backend.YoutubeAPI.captionDownload import CaptionDownload
from backend.YoutubeAPI.credentials import YoutubeCredentials
from backend.YoutubeAPI.speech2text import Speech2Text
from backend.YoutubeAPI.video2audio import Video2audio
from backend.models import Lezioni


class ParseVideo():

    def __init__(self, lezione) -> None:
        self.lezione = Lezioni.objects.get(pk=lezione['id'])
        self.directoryName = self.createDirectory(lezione["nome"])
        self.usableCaption = ''



    def createDirectory(self, directoryName: str):
        print(os.path.isdir(directoryName))
        print(directoryName)
        if not os.path.isdir('Outputs/' + directoryName):
            Path('Outputs/' + directoryName).mkdir(parents=True, exist_ok=True)
            return directoryName
        else:
            return self.createDirectory(directoryName + self.randomword())

    def randomword(self):
        letters = string.ascii_lowercase
        return '_' + ''.join(random.choice(letters) for i in range(4))

    def getCaptionFromVideo(self, videoName: str, pathCredentials: str):
        speech = Speech2Text(pathCredentials)
        Video2audio().processVideo(videoName)
        audioName = videoName.replace("Video", "Audio", 1) + '.flac'
        speech.upload_blob(audioName)
        speech.sample_long_running_recognize(audioName)
        speech.delete_blob(audioName)
        self.usableCaption = speech.generateFile(self.directoryName)
        return self

    def getCaptionFromID(self, videoID: str, client_secretPATH: str):
        credentials = YoutubeCredentials(client_secretPATH).get()

        CaptionDownload(credentials).get(videoID, self.directoryName)

        cropCaption = CropCaption(self.directoryName)

        self.usableCaption = cropCaption.getUsableCaption()
        cropCaption.generateFile()
        return self

    def getCaptionFromFile(self, captionFileName: str):
        captionFile = open(captionFileName, 'r')
        self.usableCaption = captionFile.read()
        return self

    def parseFromCaption(self, posTag=['']):
        tokenizer = Tokenize(self.usableCaption)
        sentencesWithToken = tokenizer.getTokens()
        tokenizer.generateFile(directoryName=self.directoryName)

        self.parse(posTag, sentencesWithToken)

    def parseFromTokenFile(self, posTag=['']):
        sentencesWithToken = []
        with open('Outputs/' + self.directoryName + '/token.csv') as f:
            next(f)
            token = [line.strip().split(';') for line in f]
            for data in token:
                sentencesWithToken.append({
                    'word': data[0],
                    'time': data[1],
                    'pos': data[2],
                })

        self.parse(posTag, sentencesWithToken)


    def parse(self, posTag, sentencesWithToken):

        findBinomi = FindBinomi(sentencesWithToken)
        findBinomi.searchForTwo(lezione=self.lezione, posTag=posTag)
        findBinomi.generateFile(directoryName=self.directoryName)

        prioritize = Prioritize(sentencesWithToken)
        prioritize.getOrdered(lezione=self.lezione, posTag=posTag)
        prioritize.generateFile(directoryName=self.directoryName)

        breakAnalyzer = BreakAnalyzer(sentencesWithToken)
        breakAnalyzer.getBreaks()
        breakAnalyzer.generateFile(directoryName=self.directoryName)

        lda = LDA()
        lda.findTopic(sentencesWithToken, posTag=posTag, nTopic=8)
        lda.generateFile(directoryName=self.directoryName)
        #lda.display()
