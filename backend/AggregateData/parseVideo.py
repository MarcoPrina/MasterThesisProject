from backend.AggregateData.findBinomi import FindBinomi
from backend.AggregateData.lda import LDA
from backend.AggregateData.prioritize import Prioritize
from backend.AggregateData.tokenize import Tokenize
from backend.YoutubeAPI.speech2text import Speech2Text
from backend.YoutubeAPI.video2audio import Video2audio


class ParseVideo:

    def __init__(self) -> None:
        self.lda = LDA()
        self.prioritize = Prioritize()
        self.findBinomi = FindBinomi()
        self.usableCaption = ''

    def getCaptionFromVideo(self, videoName: str, pathCredentials: str):
        speech = Speech2Text(pathCredentials)
        Video2audio().processVideo(videoName)
        audioName = videoName.replace("Video", "Audio", 1) + '.flac'
        speech.upload_blob(audioName)
        speech.recognize_audio(audioName)
        speech.delete_blob(audioName)
        self.usableCaption = speech.generate_captions()
        return self

    def getCaptionFromFile(self, captionFileName: str):
        captionFile = open(captionFileName, 'r')
        self.usableCaption = captionFile.read()
        return self

    def parseFromCaption(self, posTag=['']):
        tokenizer = Tokenize(self.usableCaption)
        sentencesWithToken = tokenizer.getTokens()

        self.parse(posTag, sentencesWithToken)

    def parseFromTokenFile(self, token_path, posTag=['']):
        sentencesWithToken = []
        with open(token_path) as f:
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
        self.findBinomi.searchForTwo(sentencesWithToken, posTag=posTag)
        self.prioritize.getOrdered(sentencesWithToken, posTag=posTag)
        self.lda.findTopic(sentencesWithToken, posTag=posTag, nTopic=8)

    def saveOnDB(self, lezione):
        self.findBinomi.saveOnDB(lezione=lezione)
        self.prioritize.saveOnDB(lezione=lezione)
        self.lda.saveOnDB(lezione=lezione)
