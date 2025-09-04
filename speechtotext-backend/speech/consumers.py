import json
from channels.generic.websocket import AsyncWebsocketConsumer
from tools.tool import Procedure
from tools import VoiceprintRegistration
from funasr import AutoModel
import os
import torch
import io
import numpy as np
from pydub import AudioSegment
import time

from speech.singleton import SpeechSystem

speech_system = SpeechSystem()  # 获取单例
procedure = speech_system.procedure
registration_system = speech_system.registration_system


class VoiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()


        # 初始化转录流程 + 声纹系统
        self.procedure = procedure
        self.reg_system = registration_system  # 声纹注册系统

        # 当前起始时间
        self.start_time = time.time()

        await self.send(text_data="WebSocket 已连接，模型初始化完成！")

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        """
        接收前端音频流，实时处理
        """
        if bytes_data:
            # 如果前端直接推 PCM16 流，就不需要转码
            try:
                # 假设前端传的是 PCM16 单声道 16k
                pcm_data = np.frombuffer(bytes_data, dtype=np.int16).tobytes()
            except Exception:
                # 如果前端传的是 webm/opus，就解码
                audio = AudioSegment.from_file(io.BytesIO(bytes_data), format="webm")
                pcm_data = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2).raw_data

            # 调用 Procedure，带声纹识别
            results = self.procedure.get_speech_segments_with_embeddings(
                pcm_data,
                time_start=self.start_time,
                reg_system=self.reg_system
            )

            # 构造返回内容
            response = {
                "text": " ".join([seg['text'] for seg in results]),
                "segments": results
            }
            await self.send(text_data=json.dumps(response, ensure_ascii=False))
