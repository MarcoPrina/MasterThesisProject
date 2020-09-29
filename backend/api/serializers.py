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


class WordListSerializer(serializers.ModelSerializer):
    word = serializers.SerializerMethodField('get_word')
    list = serializers.SerializerMethodField('list_word')

    class Meta:
        model = Words
        fields = ['word', 'list']

    def get_word(self, obj):
        return obj.word + '*'

    def list_word(self, obj):
        word = Words.objects.filter(word=obj.word)
        return BinomiSerializer(word, many=True).data

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Words
        fields = ['id', 'lezione', 'time_stamp']


class BinomiListSerializer(serializers.ModelSerializer):
    word = serializers.SerializerMethodField('get_binomio_name')
    list = serializers.SerializerMethodField('list_binomi')

    class Meta:
        model = Binomi
        fields = ['word', 'list']

    def get_binomio_name(self, obj):
        return obj.word1 + '* ' + obj.word2 + '*'

    def list_binomi(self, obj):
        binomi = Binomi.objects.filter(word1=obj.word1, word2=obj.word2)
        return BinomiSerializer(binomi, many=True).data


class BinomiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Binomi
        fields = ['id', 'lezione', 'time_stamp']
