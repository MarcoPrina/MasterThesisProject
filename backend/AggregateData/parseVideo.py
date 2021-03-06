import logging
import os
import threading
import urllib.parse as urlparse
from urllib.parse import parse_qs

from django.db import transaction

from backend.AggregateData.cropCaption import CropCaption
from backend.AggregateData.findBinomi import FindBinomi
from backend.AggregateData.findwords import FindWords
from backend.AggregateData.lda import LDA
from backend.AggregateData.tokenize import Tokenize
from backend.ExternalAPI.captionDownload import CaptionDownload
from backend.ExternalAPI.vimeoDownload import VimeoDownload
from backend.ExternalAPI.youtubeCredentials import YoutubeCredentials
from backend.ExternalAPI.speech2text import Speech2Text
from backend.AggregateData.video2audio import Video2audio


class ParseVideo:

    def __init__(self) -> None:
        self.tokenizer = Tokenize()
        self.lda = LDA()
        self.findWords = FindWords()
        self.findBinomi = FindBinomi()
        self.usableCaption = ''
        self.posTag = ['S', 'A']

    def getCaptionFromYoutubeID(self, videoID: str, client_secretPATH: str):
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

    def parse(self, process_lda):
        tokenizedLesson = self.tokenizer.getTokens(self.usableCaption)

        self.findBinomi.searchForTwo(tokenizedLesson, posTag=self.posTag)
        self.findWords.search(tokenizedLesson, posTag=self.posTag)
        if process_lda:
            self.lda.findTopicFromTokens(tokenizedLesson, posTag=self.posTag, nTopic=16)

    def saveOnDB(self, lezione, process_lda):
        self.tokenizer.saveOnDB(lezione=lezione, posTag=self.posTag)
        self.findBinomi.saveOnDB(lezione=lezione)
        self.findWords.saveOnDB(lezione=lezione)
        if process_lda:
            self.lda.saveOnDBLezione(lezione=lezione)


class AnalyzeVideo(threading.Thread):
    logger = logging.getLogger(__name__)
    googleCredential = 'Credentials/credentials_googleCloud.json'
    youtubeCredential = 'Credentials/client_secret_youtube.json'
    vimeoCredential = 'Credentials/vimeo_credential.txt'

    def __init__(self, lezione):
        threading.Thread.__init__(self)
        self.lezione = lezione

    def run(self):
        try:
            parser = ParseVideo()
            if self.lezione.video.name:
                parser.getCaptionFromVideo(self.lezione.video.name, self.googleCredential)
                os.remove(self.lezione.video.name)
                os.remove(self.lezione.video.name.replace("Video", "Audio", 1) + '.flac')
            elif 'youtube' in self.lezione.video_url:
                parsed = urlparse.urlparse(self.lezione.video_url)
                videoID = parse_qs(parsed.query)['v'][0]
                parser.getCaptionFromYoutubeID(videoID, self.youtubeCredential)
                # parser.getCaptionFromFile('/home/marco/PycharmProjects/AggregateData/Outputs/1/caption.txt')
            else:
                videoID = self.lezione.video_url.split('/')[-1]
                VimeoDownload(self.vimeoCredential).get(videoID)
                parser.getCaptionFromVideo('Media/Video/' + videoID + '.mp4', self.googleCredential)
                os.remove('Media/Video/' + videoID + '.mp4')
                os.remove('Media/Audio/' + videoID + '.mp4' + '.flac')

            parser.parse(process_lda=self.lezione.process_lda)

            with transaction.atomic():
                parser.saveOnDB(lezione=self.lezione, process_lda=self.lezione.process_lda)

                self.lezione.processata = True
                self.lezione.save()

        except Exception as e:
            self.logger.error('Errore analizzando la lezione "%s" del corso "%s"',
                              self.lezione.nome,
                              self.lezione.corso.nome,
                              exc_info=e)
