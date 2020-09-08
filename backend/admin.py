from django.contrib import admin

from .models import Corsi, Lezioni, Binomi, Words

admin.site.register(Corsi)
admin.site.register(Lezioni)
admin.site.register(Binomi)
admin.site.register(Words)
