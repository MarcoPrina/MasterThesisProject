from ..models import Corsi
from rest_framework import serializers


class CorsoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corsi
        fields = ['id', 'kiro_url', 'nome']
