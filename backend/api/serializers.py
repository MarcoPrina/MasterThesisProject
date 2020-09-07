from ..models import Corsi, Lezioni
from rest_framework import serializers


class CorsoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corsi
        fields = ['id', 'kiro_url', 'nome']


class LezioneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lezioni
        fields = ['id', 'video_url', 'nome', 'corso']
