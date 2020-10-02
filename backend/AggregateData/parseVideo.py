import logging
import threading

from django.db import transaction

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


class AnalyzeVideo(threading.Thread):
    logger = logging.getLogger(__name__)

    def __init__(self, video_path, lezione):
        threading.Thread.__init__(self)
        self.video_path = video_path
        self.lezione = lezione

    def run(self):
        try:
            self.lezione.save()
            # pattern = re.compile(r"\w")
            # res = re.sub("[A-Za-z]+", "", self.input_data['nome'])
            parser = ParseVideo() \
                .getCaptionFromFile('/home/marco/PycharmProjects/AggregateData/Outputs/1/caption.txt')
            #    .getCaptionFromVideo(self.video_path, 'backend/YoutubeAPI/credentials.json')

            parser.parseFromCaption(posTag=['S', 'A'])

            with transaction.atomic():
                parser.saveOnDB(lezione=self.lezione)
                self.lezione.processata = True
                self.lezione.save()

        except Exception as e:
            self.logger.error('Errore analizzando il corso "%s" nella lezione"%s"',
                              self.lezione.data['corso'],
                              self.lezione.data['nome'],
                              exc_info=e)

        # os.remove(self.video_path)
        # os.remove(self.video_path.replace("Video", "Audio", 1) + '.flac')
