import os
import torch
from funasr import AutoModel
from speech.tools.tool import Procedure
from speech.tools.VoiceprintRegistration import VoiceprintRegistration
import psutil

class SpeechSystem:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpeechSystem, cls).__new__(cls)
            cls._instance._init_models()
        return cls._instance

    def _init_models(self):
        home_directory = os.path.expanduser("~")
        device = "cuda" if torch.cuda.is_available() else "cpu"

        asr_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                                      "speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch")
        vad_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                                      "speech_fsmn_vad_zh-cn-16k-common-pytorch")
        punc_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                                       "punc_ct-transformer_zh-cn-common-vocab272727-pytorch")
        spk_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                                      "speech_campplus_sv_zh-cn_16k-common")

        # 初始化 AutoModel
        self.model = AutoModel(
            model=asr_model_path,
            vad_model=vad_model_path,
            punc_model=punc_model_path,
            spk_model=spk_model_path,
            ngpu=1,
            ncpu=psutil.cpu_count(),
            device=device,
            disable_pbar=True,
            disable_log=True,
            disable_update=True
        )

        # 初始化处理流程和声纹注册系统
        self.procedure = Procedure(self.model)
        self.registration_system = VoiceprintRegistration(self.model)

        print(f"SpeechSystem 单例初始化完成，设备: {device}")
