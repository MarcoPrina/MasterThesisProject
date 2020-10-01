from ..models import Corsi, Lezioni, Words, Binomi
from rest_framework import serializers


class CorsoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corsi
        fields = ['id', 'kiro_url', 'nome']


class LezioneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lezioni
        fields = ['id', 'kiro_url', 'nome', 'corso']


class WordListSerializer(serializers.ModelSerializer):
    word = serializers.SerializerMethodField('get_word')
    list = serializers.SerializerMethodField('list_word')

    class Meta:
        model = Words
        fields = ['word', 'list']

    def get_word(self, obj):
        return obj.word + '*'

    def list_word(self, obj):
        corso = self.context.get("corso")
        lezione = self.context.get("lezione")
        if lezione:
            word = Words.objects.filter(word=obj.word, lezione=lezione)
        else:
            word = Words.objects.filter(word=obj.word, lezione__corso=corso)
        return BinomiSerializer(word, many=True).data


class WordSerializer(serializers.ModelSerializer):
    lezione = LezioneSerializer()

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
        corso = self.context.get("corso")
        lezione = self.context.get("lezione")
        if lezione:
            binomi = Binomi.objects.filter(word1=obj.word1, word2=obj.word2, lezione=lezione)
        else:
            binomi = Binomi.objects.filter(word1=obj.word1, word2=obj.word2, lezione__corso=corso)
        return BinomiSerializer(binomi, many=True).data


class BinomiSerializer(serializers.ModelSerializer):
    lezione = LezioneSerializer()

    class Meta:
        model = Binomi
        fields = ['id', 'lezione', 'lezione', 'time_stamp']
