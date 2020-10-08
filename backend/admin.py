from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .AggregateData.parseVideo import AnalyzeVideo
from .models import Corso, Lezione, Binomio, Word, BinomioCountForLesson, WordCountForLesson, LdaTopic, LdaWord, \
    WordCountForCourse, BinomioCountForCourse


class MyAdminSite(AdminSite):
    site_header = 'Gestione corsi e lezioni'
    site_title = 'Unipv'
    index_title = 'Analisi corsi'
    site_url = None


admin_site = MyAdminSite(name='admin')


class LezioniAdminForm(forms.ModelForm):
    def clean(self):
        if not len(self.errors) > 0:
            if self.cleaned_data['video_url'] is None and self.cleaned_data['video'] is None:
                raise ValidationError(_("Serve inserire o l'url del video o caricarlo direttamente"))
            if self.cleaned_data['video_url'] is not None and \
                    'youtube' not in self.cleaned_data['video_url'] and\
                    'vimeo' not in self.cleaned_data['video_url']:
                raise ValidationError(_("I link devono essere o di youtube o di vimeo"))


class LezioniAdmin(admin.ModelAdmin):
    form = LezioniAdminForm
    fields = ('corso', 'nome', 'kiro_url', ('video_url', 'video'), ('process_lda', 'process_corso'), 'processata')
    readonly_fields = ('processata',)
    list_display = ('nome', 'corso', 'video_url', 'kiro_url')
    search_fields = ['nome']

    def save_model(self, request, obj, form, change):
        obj.save()
        AnalyzeVideo(obj).start()


class CorsiAdmin(admin.ModelAdmin):
    list_display = ('nome', 'kiro_url')
    search_fields = ['nome']


def join_binomio(obj):
    return "%s %s" % (obj.word1, obj.word2)


join_binomio.short_description = 'Binomio'


class BinomiAdmin(admin.ModelAdmin):
    list_display = (join_binomio, 'lezione',)
    search_fields = ['word1', 'word2']


class BinomiCountLessonAdmin(admin.ModelAdmin):
    list_display = ('binomio', 'lezione', 'count')
    search_fields = ['binomio']


class BinomiCountCourseAdmin(admin.ModelAdmin):
    list_display = ('binomio', 'corso', 'count')
    search_fields = ['binomio']


class WordsAdmin(admin.ModelAdmin):
    list_display = ('word', 'lezione',)
    search_fields = ['word']


class WordsCountLessonAdmin(admin.ModelAdmin):
    list_display = ('word', 'lezione', 'count')
    search_fields = ['word']


class WordsCountCorsoAdmin(admin.ModelAdmin):
    list_display = ('word', 'corso', 'count')
    search_fields = ['word']


class LdaWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'ldaTopic', 'weight')
    search_fields = ['word']


admin_site.register(Lezione, LezioniAdmin)
admin_site.register(Corso, CorsiAdmin)
admin_site.register(Binomio, BinomiAdmin)
admin_site.register(BinomioCountForLesson, BinomiCountLessonAdmin)
admin_site.register(BinomioCountForCourse, BinomiCountCourseAdmin)
admin_site.register(Word, WordsAdmin)
admin_site.register(WordCountForLesson, WordsCountLessonAdmin)
admin_site.register(WordCountForCourse, WordsCountCorsoAdmin)
admin_site.register(LdaTopic)
admin_site.register(LdaWord, LdaWordAdmin)
