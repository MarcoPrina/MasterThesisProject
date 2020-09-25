import json
import logging
import os
import re
import threading

from django.contrib import admin
from django import forms
from django.db import transaction

from .AggregateData.parseVideo import ParseVideo
from .models import Corsi, Lezioni, Binomi, Words, BinomiCount, WordsCount, LdaTopic, LdaWord


class LezioniAdmin(admin.ModelAdmin):
    # form = LezioniForm
    list_display = ('corso', 'nome', 'video_url', 'kiro_url')

    def save_model(self, request, obj, form, change):
        video_path = ''
        AnalyzeVideo(video_path, obj).start()


class AnalyzeVideo(threading.Thread):
    logger = logging.getLogger(__name__)

    def __init__(self, video_path, lezione):
        threading.Thread.__init__(self)
        self.video_path = video_path
        self.lezione = lezione

    def run(self):
        try:
            # pattern = re.compile(r"\w")
            # res = re.sub("[A-Za-z]+", "", self.input_data['nome'])
            parser = ParseVideo() \
                .getCaptionFromFile('/home/marco/PycharmProjects/AggregateData/Outputs/1/caption.txt')
            #    .getCaptionFromVideo(self.video_path, 'backend/YoutubeAPI/credentials.json')

            parser.parseFromCaption(posTag=['S', 'A'])

            with transaction.atomic():
                self.lezione.save()
                parser.saveOnDB(lezione=self.lezione)
                self.lezione.processata = True
                self.lezione.save()

        except Exception as e:
            self.logger.error('Error analyzing video of "%s" corso in "%s" lesson',
                              self.lezione.data['corso'],
                              self.lezione.data['nome'],
                              exc_info=e)

        # os.remove(self.video_path)
        # os.remove(self.video_path.replace("Video", "Audio", 1) + '.flac')


admin.site.register(Lezioni, LezioniAdmin)

admin.site.register(Corsi)
admin.site.register(Binomi)
admin.site.register(BinomiCount)
admin.site.register(Words)
admin.site.register(WordsCount)
admin.site.register(LdaTopic)
admin.site.register(LdaWord)
