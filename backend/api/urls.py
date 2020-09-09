from django.urls import path

from .views import NewLezione, CorsiAPIView

app_name = 'account'

urlpatterns = [

    path('lezione', NewLezione.as_view(), name='new_lezione'),
    path('corso', CorsiAPIView.as_view(), name='new_corso'),

]