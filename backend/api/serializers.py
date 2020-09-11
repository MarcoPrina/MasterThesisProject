from ..models import Corsi, Lezioni, Words, Binomi
from rest_framework import serializers


class CorsoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corsi
        fields = ['id', 'kiro_url', 'nome']


class LezioneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lezioni
        fields = ['id', 'video_url', 'kiro_url', 'nome', 'corso']


class WordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Words
        fields = ['id', 'word', 'lezione', 'time_stamp']

class BinomiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Binomi
        fields = ['id', 'word1', 'word2', 'lezione', 'time_stamp']
