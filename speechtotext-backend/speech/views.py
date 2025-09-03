import json

import requests
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
from .serializers import MeetingSerializer, VoiceprintSerializer

# 初始化模型（只加载一次，避免每次请求都加载）
home_directory = os.path.expanduser("~")
asr_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                              "speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch")
vad_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                              "speech_fsmn_vad_zh-cn-16k-common-pytorch")
punc_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                               "punc_ct-transformer_zh-cn-common-vocab272727-pytorch")
spk_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                              "speech_campplus_sv_zh-cn_16k-common")

model = AutoModel(
    model=asr_model_path,
    vad_model=vad_model_path,
    punc_model=punc_model_path,
    spk_model=spk_model_path,
    ngpu=1,
    ncpu=psutil.cpu_count(),
    device="cuda" if torch.cuda.is_available() else "cpu",
    disable_pbar=True,
    disable_log=True,
    disable_update=True,
)
procedure = Procedure(model)

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
        results = procedure.get_speech_segments_with_embeddings(audio_bytes, time_start=0)

        return JsonResponse({"results": results}, safe=False)
    return JsonResponse({"error": "请用 POST 上传 audio 文件"}, status=400)


# 会议记录管理
class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all().order_by('-created_at')
    serializer_class = MeetingSerializer


# 声纹管理
class VoiceprintViewSet(viewsets.ModelViewSet):
    queryset = Voiceprint.objects.all().order_by('-upload_date')
    serializer_class = VoiceprintSerializer