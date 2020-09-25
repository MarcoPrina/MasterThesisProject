from django.urls import path

from .views import CorsiAPIView, CorsoDetails, RetriveWords, Search

app_name = 'account'

urlpatterns = [

    path('corso', CorsiAPIView.as_view(), name='new_corso'),
    path('corso/<int:pk>/', CorsoDetails.as_view(), name='corso_detail'),
    path('words/', RetriveWords.as_view(), name='retrive_words'),
    path('search/', Search.as_view(), name='search_for_words'),

]