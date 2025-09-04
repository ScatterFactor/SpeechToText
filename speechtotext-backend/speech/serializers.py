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

class VoiceprintListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voiceprint
        fields = ["id", "speaker_name", "audio_filename", "upload_date"]