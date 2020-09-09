from django.urls import path

from .views import NewLezione, CorsiAPIView, CorsoDetails, RetriveWords, RetriveBinomi

app_name = 'account'

urlpatterns = [

    path('lezione', NewLezione.as_view(), name='new_lezione'),
    path('corso', CorsiAPIView.as_view(), name='new_corso'),
    path('corso/<int:pk>/', CorsoDetails.as_view(), name='corso_detail'),
    path('words/', RetriveWords.as_view(), name='retrive_words'),
    path('binomi/', RetriveBinomi.as_view(), name='retrive_binomi'),

]