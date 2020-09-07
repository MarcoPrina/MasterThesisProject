from django.urls import path

from .views import NewLezione, NewCorso

app_name = 'account'

urlpatterns = [

    path('lezione', NewLezione.as_view(), name='new_lezione'),
    path('corso', NewCorso.as_view(), name='new_corso'),

]