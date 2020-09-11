from django.contrib import admin

from .models import Corsi, Lezioni, Binomi, Words, BinomiCount

admin.site.register(Corsi)
admin.site.register(Lezioni)
admin.site.register(Binomi)
admin.site.register(BinomiCount)
admin.site.register(Words)
