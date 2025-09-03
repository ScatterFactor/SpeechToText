from rest_framework import serializers
from .models import Meeting, Voiceprint

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'

class VoiceprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voiceprint
        fields = '__all__'
