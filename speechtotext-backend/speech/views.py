import json
import subprocess
import os

import requests

import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os, torch, psutil
from funasr import AutoModel
from speech.tools.tool import Procedure   # 直接引入你的类

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import Meeting, Voiceprint
from .serializers import MeetingSerializer, VoiceprintSerializer, VoiceprintListSerializer
from .tools.VoiceprintRegistration import VoiceprintRegistration

from speech.singleton import SpeechSystem

speech_system = SpeechSystem()  # 获取单例
procedure = speech_system.procedure
registration_system = speech_system.registration_system



DEEPSEEK_API_KEY = "sk-7cde7a227357449ebc8077b457b4e8ba"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"  # 假设是这个地址


@api_view(['POST'])
def summarize_content(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            content = data.get("content", "")
            if not content:
                return JsonResponse({"error": "content不能为空"}, status=400)

            # 构建请求给 Deepseek API
            payload = {
                "model": "deepseek-chat",
                "stream": False,
                "messages": [
                    {"role": "system", "content": "你是一个专业的会议总结助手，请只返回纯文本摘要，不要 Markdown，不要编号列表，只用自然段描述。"},
                    {"role": "user", "content": content}
                ]
            }
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)
            response_data = response.json()

            # 解析 Deepseek 返回结果，这里假设返回结构里摘要在 choices[0].message.content
            summary = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

            return JsonResponse({"summary": summary})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "只支持POST请求"}, status=405)

@api_view(['POST'])
def recognize(request):
    if request.method == "POST" and request.FILES.get("audio"):
        audio_file = request.FILES["audio"]
        audio_bytes = audio_file.read()
        results = procedure.get_speech_segments_with_embeddings(audio_bytes, time_start=0,reg_system = registration_system)
        return JsonResponse({"results": results}, safe=False)
    return JsonResponse({"error": "请用 POST 上传 audio 文件"}, status=400)

# 会议记录管理
class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all().order_by('-created_at')
    serializer_class = MeetingSerializer









# -------------------------
# 加载数据库中已有声纹
# -------------------------
for record in Voiceprint.objects.all():
    # 将 JSON 字段转回 tensor
    embedding_tensor = torch.tensor(record.embedding, dtype=torch.float32)
    registration_system.speakers.setdefault(record.speaker_name, []).append(embedding_tensor)

# -------------------------
# DRF ViewSet
# -------------------------
class VoiceprintViewSet(viewsets.ModelViewSet):
    queryset = Voiceprint.objects.all().order_by('-upload_date')
    serializer_class = VoiceprintSerializer

    def list(self, request, *args, **kwargs):
        self.serializer_class = VoiceprintListSerializer
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        speaker_name = request.data.get('speaker_name')
        audio_file = request.FILES.get('audio_file')
        audio_filename = request.data.get('audio_filename', '')

        if not speaker_name or not audio_file:
            return Response({"error": "speaker_name 和 audio_file 必填"}, status=status.HTTP_400_BAD_REQUEST)

        # 读取前端上传的音频 bytes
        audio_bytes_raw = audio_file.read()

        # 先写临时文件
        with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as tmp_file:
            tmp_file.write(audio_bytes_raw)
            tmp_file.flush()
            tmp_input_path = tmp_file.name

        # 解码成 PCM16 WAV bytes
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav_file:
            tmp_wav_path = tmp_wav_file.name

        subprocess.run([
            "ffmpeg", "-y", "-i", tmp_input_path, "-ac", "1", "-ar", "16000",
            "-f", "wav", tmp_wav_path
        ], check=True)

        with open(tmp_wav_path, "rb") as f:
            audio_bytes = f.read()

        # 删除临时文件
        os.remove(tmp_input_path)
        os.remove(tmp_wav_path)

        # 调用 bytes_to_speaker 判断是否已经注册
        recognized_speaker = registration_system.bytes_to_speaker(audio_bytes, threshold=0.6)

        # 如果是新说话人或者想更新 embedding
        if recognized_speaker != speaker_name:
            # 使用 register 提取 embedding 并存入 speakers
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file.flush()
                tmp_path = tmp_file.name

            try:
                registration_system.register(tmp_path, speaker_name)
            finally:
                os.remove(tmp_path)  # 手动删除临时文件

        # 获取最新 embedding
        embeddings_list = registration_system.speakers.get(speaker_name, [])
        if not embeddings_list:
            return Response({"error": "未能生成有效 embedding"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        embedding_tensor = embeddings_list[-1]
        embedding_list = embedding_tensor.detach().cpu().numpy().tolist()  # 转成 list 保存

        # 保存数据库
        voiceprint_data = {
            "speaker_name": speaker_name,
            "embedding": embedding_list,
            "audio_filename": audio_filename
        }

        serializer = self.get_serializer(data=voiceprint_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)