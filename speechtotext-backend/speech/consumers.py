import json
from channels.generic.websocket import AsyncWebsocketConsumer
from tools.tool import Procedure  # 你保存 Procedure 的文件名
from funasr import AutoModel
import os
import torch
import asyncio

class VoiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # 初始化 ASR + VAD + SPK 模型
        home = os.path.expanduser("~")
        asr_model_path = os.path.join(home, ".cache/modelscope/hub/models/iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch")
        vad_model_path = os.path.join(home, ".cache/modelscope/hub/models/iic/speech_fsmn_vad_zh-cn-16k-common-pytorch")
        punc_model_path = os.path.join(home, ".cache/modelscope/hub/models/iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch")
        spk_model_path = os.path.join(home, ".cache/modelscope/hub/models/iic/speech_campplus_sv_zh-cn-16k-common")

        device = "cuda" if torch.cuda.is_available() else "cpu"

        model = AutoModel(
            model=asr_model_path,
            vad_model=vad_model_path,
            punc_model=punc_model_path,
            spk_model=spk_model_path,
            device=device,
            disable_pbar=True,
            disable_log=True,
            disable_update=True
        )

        self.procedure = Procedure(model)
        await self.send(text_data="WebSocket 已连接，模型初始化完成！")

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        """
        接收前端发送的音频字节流
        """
        if bytes_data:
            # 获取前端发送的音频 bytes
            audio_bytes = bytes_data
            timestamp_now = int(torch.tensor(0).item())  # 可以自己改成真实时间戳

            # 调用 Procedure 处理音频，返回文本 + 声纹 embedding
            results = self.procedure.get_speech_segments_with_embeddings(audio_bytes, timestamp_now)

            # 构建返回内容，只返回文本
            texts = [seg['text'] for seg in results]
            response = {
                "text": " ".join(texts),
                "segments": [
                    {
                        "text": seg['text'],
                        "time": seg['time']
                    } for seg in results
                ]
            }
            await self.send(text_data=json.dumps(response))
