from django.contrib import admin

from .models import Corsi, Lezioni, Binomi, Words, BinomiCount, WordsCount, LdaTopic, LdaWord

admin.site.register(Corsi)
admin.site.register(Lezioni)
admin.site.register(Binomi)
admin.site.register(BinomiCount)
admin.site.register(Words)
admin.site.register(WordsCount)
admin.site.register(LdaTopic)
admin.site.register(LdaWord)
