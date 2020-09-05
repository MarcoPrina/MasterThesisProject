from django.urls import path

from .views import UploadVideo

app_name = 'account'

urlpatterns = [

    path('video', UploadVideo.as_view(), name='upload_video'),

]