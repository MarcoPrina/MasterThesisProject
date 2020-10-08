from rest_framework import serializers

from ..models import Corso, Lezione, Word, Binomio


class CorsoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corso
        fields = ['id', 'kiro_url', 'nome']


class LezioneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lezione
        fields = ['id', 'kiro_url', 'nome', 'corso']


class WordListSerializer(serializers.ModelSerializer):
    word = serializers.SerializerMethodField('get_word')
    list = serializers.SerializerMethodField('list_word')

    class Meta:
        model = Word
        fields = ['word', 'list']

    def get_word(self, obj):
        return obj.word + '*'

    def list_word(self, obj):
        corso = self.context.get("corso")
        lezione = self.context.get("lezione")
        if lezione:
            word = Word.objects.filter(word=obj.word, lezione=lezione)
        else:
            word = Word.objects.filter(word=obj.word, lezione__corso=corso)
        return BinomiSerializer(word, many=True).data


class WordSerializer(serializers.ModelSerializer):
    lezione = LezioneSerializer()

    class Meta:
        model = Word
        fields = ['id', 'lezione', 'time_stamp']


class BinomiListSerializer(serializers.ModelSerializer):
    word = serializers.SerializerMethodField('get_binomio_name')
    list = serializers.SerializerMethodField('list_binomi')

    class Meta:
        model = Binomio
        fields = ['word', 'list']

    def get_binomio_name(self, obj):
        return obj.word1 + '* ' + obj.word2 + '*'

    def list_binomi(self, obj):
        corso = self.context.get("corso")
        lezione = self.context.get("lezione")
        if lezione:
            binomi = Binomio.objects.filter(word1=obj.word1, word2=obj.word2, lezione=lezione)
        else:
            binomi = Binomio.objects.filter(word1=obj.word1, word2=obj.word2, lezione__corso=corso)
        return BinomiSerializer(binomi, many=True).data


class BinomiSerializer(serializers.ModelSerializer):
    lezione = LezioneSerializer()

    class Meta:
        model = Binomio
        fields = ['id', 'lezione', 'time_stamp']
