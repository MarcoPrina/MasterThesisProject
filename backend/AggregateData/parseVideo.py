import logging
import threading
import os

import urllib.parse as urlparse
from urllib.parse import parse_qs

from django.db import transaction

from backend.AggregateData.cropCaption import CropCaption
from backend.AggregateData.findBinomi import FindBinomi
from backend.AggregateData.lda import LDA
from backend.AggregateData.prioritize import Prioritize
from backend.AggregateData.tokenize import Tokenize
from backend.YoutubeAPI.captionDownload import CaptionDownload
from backend.YoutubeAPI.credentials import YoutubeCredentials
from backend.YoutubeAPI.speech2text import Speech2Text
from backend.YoutubeAPI.video2audio import Video2audio


class ParseVideo:

    def __init__(self) -> None:
        self.lda = LDA()
        self.prioritize = Prioritize()
        self.findBinomi = FindBinomi()
        self.usableCaption = ''

    def getCaptionFromID(self, videoID: str, client_secretPATH: str):
        credentials = YoutubeCredentials(client_secretPATH).get()

        CaptionDownload(credentials).get(videoID)

        cropCaption = CropCaption(videoID)

        self.usableCaption = cropCaption.getUsableCaption()
        return self

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

    def parse(self, process_lda, posTag=['']):
        tokenizer = Tokenize(self.usableCaption)
        sentencesWithToken = tokenizer.getTokens()

        self.findBinomi.searchForTwo(sentencesWithToken, posTag=posTag)
        self.prioritize.getOrdered(sentencesWithToken, posTag=posTag)
        if process_lda:
            self.lda.findTopic(sentencesWithToken, posTag=posTag, nTopic=8)

    def saveOnDB(self, lezione, process_lda):
        self.findBinomi.saveOnDB(lezione=lezione)
        self.prioritize.saveOnDB(lezione=lezione)
        if process_lda:
            self.lda.saveOnDB(lezione=lezione)


class AnalyzeVideo(threading.Thread):
    logger = logging.getLogger(__name__)

    def __init__(self, lezione):
        threading.Thread.__init__(self)
        self.lezione = lezione

    def run(self):
        try:
            parser = ParseVideo()
            if self.lezione.video.name is not None:
                parser.getCaptionFromVideo(self.lezione.video.name, 'Credentials/credentials_googleCloud.json')
                os.remove(self.lezione.video.name)
                os.remove(self.lezione.video.name.replace("Video", "Audio", 1) + '.flac')
            elif 'youtube' in self.lezione.video_url:
                parsed = urlparse.urlparse(self.lezione.video_url)
                videoID = parse_qs(parsed.query)['v'][0]
                parser.getCaptionFromID(videoID, 'Credentials/client_secret_youtube.json')
            else:
                parser.getCaptionFromFile('/home/marco/PycharmProjects/AggregateData/Outputs/1/caption.txt')

            parser.parse(process_lda=self.lezione.process_lda, posTag=['S', 'A'])

            with transaction.atomic():
                parser.saveOnDB(lezione=self.lezione, process_lda=self.lezione.process_lda)
                self.lezione.processata = True
                self.lezione.save()

        except Exception as e:
            self.logger.error('Errore analizzando il corso "%s" nella lezione"%s"',
                              self.lezione.corso.nome,
                              self.lezione.nome,
                              exc_info=e)
