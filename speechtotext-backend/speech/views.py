from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os, torch, psutil
from funasr import AutoModel
from tools.tool import Procedure   # 直接引入你的类

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

@csrf_exempt
def recognize(request):
    if request.method == "POST" and request.FILES.get("audio"):
        audio_file = request.FILES["audio"]
        audio_bytes = audio_file.read()
        results = procedure.get_speech_segments_with_embeddings(audio_bytes, time_start=0)

        return JsonResponse({"results": results}, safe=False)
    return JsonResponse({"error": "请用 POST 上传 audio 文件"}, status=400)
