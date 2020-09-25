from django.contrib import admin

from .AggregateData.parseVideo import AnalyzeVideo
from .models import Corsi, Lezioni, Binomi, Words, BinomiCount, WordsCount, LdaTopic, LdaWord


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


admin.site.register(Lezioni, LezioniAdmin)
admin.site.register(Corsi, CorsiAdmin)
admin.site.register(Binomi, BinomiAdmin)
admin.site.register(BinomiCount, BinomiCountAdmin)
admin.site.register(Words, WordsAdmin)
admin.site.register(WordsCount, WordsCountAdmin)
admin.site.register(LdaTopic)
admin.site.register(LdaWord, LdaWordAdmin)
