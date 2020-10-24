from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from django_better_admin_arrayfield.forms.fields import DynamicArrayField
from django_better_admin_arrayfield.forms.widgets import DynamicArrayTextareaWidget, DynamicArrayWidget
from django_better_admin_arrayfield.models.fields import ArrayField

from .AggregateData.aggregateVideos import AggregateVideos
from .AggregateData.parseVideo import AnalyzeVideo
from .models import Corso, Lezione, Binomio, Word, BinomioCountForLesson, WordCountForLesson, \
    WordCountForCourse, BinomioCountForCourse, Sentence, LdaCorso, LdaLezione


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
                    'youtube' not in self.cleaned_data['video_url'] and \
                    'vimeo' not in self.cleaned_data['video_url']:
                raise ValidationError(_("I link devono essere o di youtube o di vimeo"))


class LezioniAdmin(admin.ModelAdmin):
    form = LezioniAdminForm
    fields = ('corso', 'nome', 'kiro_url', ('video_url', 'video'), 'process_lda', 'processata')
    readonly_fields = ('processata',)
    list_display = ('nome', 'corso', 'video_url', 'kiro_url')
    search_fields = ['nome']

    def save_model(self, request, obj, form, change):
        obj.save()
        AnalyzeVideo(obj).start()


class CorsiAdmin(admin.ModelAdmin):
    list_display = ('nome', 'kiro_url')
    search_fields = ['nome']

    def save_model(self, request, obj, form, change):
        obj.save()
        if obj.process_corso:
            AggregateVideos(obj).start()


def join_binomio(obj):
    return "%s %s" % (obj.word1, obj.word2)


join_binomio.short_description = 'Binomio'


class BinomiAdmin(admin.ModelAdmin):
    list_display = (join_binomio, 'lezione',)
    search_fields = ['word1', 'word2']


class BinomiCountLessonAdmin(admin.ModelAdmin):
    list_display = ('binomio', 'lezione', 'count', 'tfidf')
    list_filter = ('lezione', 'lezione__corso')
    search_fields = ['binomio']


class BinomiCountCourseAdmin(admin.ModelAdmin):
    list_display = ('binomio', 'corso', 'count')
    search_fields = ['binomio']


class WordsAdmin(admin.ModelAdmin):
    list_display = ('word', 'lezione',)
    search_fields = ['word']


class WordsCountLessonAdmin(admin.ModelAdmin):
    list_display = ('word', 'lezione', 'count', 'tfidf')
    list_filter = ('lezione', 'lezione__corso')
    search_fields = ['word']


class WordsCountCorsoAdmin(admin.ModelAdmin):
    list_display = ('word', 'corso', 'count', 'idf')
    search_fields = ['word']


class LdaWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'ldaTopic', 'weight')
    search_fields = ['word']


class SentenceAdmin(admin.ModelAdmin):
    list_display = ('lezione', 'number')


class LdaCorsoAdminForm(ModelForm):
    class Meta:
        model = LdaCorso
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lda'].widget.attrs.update(size='60')


class LdaCorsoAdmin(admin.ModelAdmin, DynamicArrayMixin):
    form = LdaCorsoAdminForm
    list_display = ['corso']


class LdaLezioneAdminForm(ModelForm):
    class Meta:
        model = LdaLezione
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lda'].widget.attrs.update(size='60')


class LdaLezioneAdmin(admin.ModelAdmin, DynamicArrayMixin):
    form = LdaLezioneAdminForm
    list_display = ['lezione']


admin_site.register(Lezione, LezioniAdmin)
admin_site.register(Corso, CorsiAdmin)
admin_site.register(Binomio, BinomiAdmin)
admin_site.register(BinomioCountForLesson, BinomiCountLessonAdmin)
admin_site.register(BinomioCountForCourse, BinomiCountCourseAdmin)
admin_site.register(Word, WordsAdmin)
admin_site.register(WordCountForLesson, WordsCountLessonAdmin)
admin_site.register(WordCountForCourse, WordsCountCorsoAdmin)
admin_site.register(LdaLezione, LdaLezioneAdmin)
admin_site.register(LdaCorso, LdaCorsoAdmin)
admin_site.register(Sentence, SentenceAdmin)
