from ..models import Corsi, Lezioni, Words, Binomi, BinomiCount
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
    wordWithAsterisk = serializers.SerializerMethodField('get_word')

    class Meta:
        model = Words
        fields = ['id', 'wordWithAsterisk', 'lezione', 'time_stamp']

    def get_word(self, obj):
        return obj.word + '*'


class BinomiSerializer(serializers.ModelSerializer):
    word = serializers.SerializerMethodField('get_binomio_name')

    class Meta:
        model = Binomi
        fields = ['id', 'word', 'lezione', 'time_stamp']

    def get_binomio_name(self, obj):
        return obj.word1 + '* ' + obj.word2 + '*'

class BinomiCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BinomiCount
        fields = ['id', 'binomio', 'lezione', 'count']
