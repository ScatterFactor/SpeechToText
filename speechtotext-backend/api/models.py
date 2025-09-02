from django.db import models

class Meeting(models.Model):
    name = models.CharField(max_length=200)
    transcription = models.TextField(blank=True)
    summary = models.JSONField(default=list, blank=True)
    audio_file = models.FileField(upload_to='recordings/')
    created_at = models.DateTimeField(auto_now_add=True)

class Voiceprint(models.Model):
    speaker_name = models.CharField(max_length=100)
    audio_file = models.FileField(upload_to='voiceprints/')
    upload_date = models.DateTimeField(auto_now_add=True)
