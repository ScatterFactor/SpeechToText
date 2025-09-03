from django.db import models

class Meeting(models.Model):
    title = models.CharField(max_length=200, verbose_name="会议标题")
    transcription = models.JSONField(default=list, blank=True, verbose_name="会议记录内容")
    summary = models.TextField(blank=True, verbose_name="会议摘要")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return self.title


class Voiceprint(models.Model):
    speaker_name = models.CharField(max_length=100, verbose_name="说话人姓名")
    embedding = models.JSONField(verbose_name="声纹向量")  # 用于比对
    audio_filename = models.CharField(max_length=255, verbose_name="音频文件名", blank=True)  # 新增音频文件名
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="录入时间")

    def __str__(self):
        return self.speaker_name
