from django.contrib import admin

from .AggregateData.parseVideo import AnalyzeVideo
from .models import Corso, Lezione, Binomio, Word, BinomioCount, WordCount, LdaTopic, LdaWord


class LezioniAdmin(admin.ModelAdmin):
    fields = ('corso', 'nome', 'video_url', 'kiro_url', 'processata')
    readonly_fields = ('processata',)
    list_display = ('nome', 'corso', 'video_url', 'kiro_url')

    def save_model(self, request, obj, form, change):
        video_path = ''
        AnalyzeVideo(video_path, obj).start()


class CorsiAdmin(admin.ModelAdmin):
    list_display = ('nome', 'kiro_url')


def join_binomio(obj):
    return "%s %s" % (obj.word1, obj.word2)


join_binomio.short_description = 'Binomio'


class BinomiAdmin(admin.ModelAdmin):
    list_display = (join_binomio, 'lezione',)


class BinomiCountAdmin(admin.ModelAdmin):
    list_display = ('binomio', 'lezione', 'count')


class WordsAdmin(admin.ModelAdmin):
    list_display = ('word', 'lezione',)


class WordsCountAdmin(admin.ModelAdmin):
    list_display = ('word', 'lezione', 'count')


class LdaWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'ldaTopic', 'weight')


admin.site.register(Lezione, LezioniAdmin)
admin.site.register(Corso, CorsiAdmin)
admin.site.register(Binomio, BinomiAdmin)
admin.site.register(BinomioCount, BinomiCountAdmin)
admin.site.register(Word, WordsAdmin)
admin.site.register(WordCount, WordsCountAdmin)
admin.site.register(LdaTopic)
admin.site.register(LdaWord, LdaWordAdmin)
