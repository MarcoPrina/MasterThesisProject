from django.urls import path

from .views import UploadVideo, NewCorso

app_name = 'account'

urlpatterns = [

    path('video', UploadVideo.as_view(), name='upload_video'),
    path('corso', NewCorso.as_view(), name='new_corso'),

]