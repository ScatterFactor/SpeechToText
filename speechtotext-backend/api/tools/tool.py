import webrtcvad
import pyaudio
import collections
import numpy as np
from funasr import AutoModel
import torch
import os
import psutil
from typing import List, Dict, Any
import time
from datetime import datetime





class Procedure(object):
    def __init__(self,model):
        hotword_file = "./hotwords.txt"
        self.model = model
        self.hotwords = ''
        if hotword_file is not None and os.path.exists(hotword_file):
            with open(hotword_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                lines = [line.strip() for line in lines]
            self.hotwords = " ".join(lines)

        print("模型加载完成。")

    def record_until_silence(self, rate=16000, chunk_ms=30, padding_ms=300):
        """
        rate：采样率
        chunk_ms：采音时间段
        padding_ms：停止发言检测时间
        从麦克风录音，直到检测到一句话结束，返回（audio_bytes,t）audio_bytes是录制时段内声音内容字符串，t为语音开始的时间戳。
        """
        vad = webrtcvad.Vad(3)  # VAD的敏感度，可以是0, 1, 2, 3。3为最高。
        chunk_size = int(rate * chunk_ms / 1000)
        num_padding_chunks = int(padding_ms / chunk_ms)
        ring_buffer = collections.deque(maxlen=num_padding_chunks)

        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=rate,
                         input=True, frames_per_buffer=chunk_size)

        print("...开始录音...")
        voiced_frames = []
        triggered = False
        timestamp1 = int(time.time())
        while True:
            frame = stream.read(chunk_size, exception_on_overflow=False)
            is_speech = vad.is_speech(frame, rate)

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > 0.9 * ring_buffer.maxlen:
                    print("检测到语音开始！")
                    triggered = True
                    voiced_frames.extend([f for f, s in ring_buffer])
                    ring_buffer.clear()
            else:
                voiced_frames.append(frame)
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                #if num_unvoiced > 0.9 * ring_buffer.maxlen:
                if num_unvoiced >  0.9* ring_buffer.maxlen:
                    print("检测到语音结束！")
                    break
        # timestamp2 = int(time.time())
        print("...录音结束...")
        stream.stop_stream()
        stream.close()
        pa.terminate()
        #
        # dt = datetime.fromtimestamp(timestamp1)
        # formatted_time1 = dt.strftime("%Y-%m-%d %H:%M:%S")
        # dt = datetime.fromtimestamp(timestamp2)
        # formatted_time2 = dt.strftime("%Y-%m-%d %H:%M:%S")
        return b"".join(voiced_frames), timestamp1#formatted_time1,formatted_time2
    def record_duration_time(self, rate=16000, chunk_ms=30, duration_sec=5):
        """
        调用函数则麦克风开始录音，持续指定时长后自动停止，返回（audio_bytes,t）audio_bytes是duration_sec时段内声音内容字符串，t为语音开始的时间戳。
        :param rate: 采样率(默认16000Hz)
        :param chunk_ms: 每次读取的音频块时长(默认30ms)
        :param duration_sec: 录音时长(秒，默认5秒)
        :return: (PCM音频数据, 开始时间, 结束时间)
        """
        chunk_size = int(rate * chunk_ms / 1000)
        total_chunks = int(duration_sec * rate / chunk_size)

        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=rate,
                         input=True, frames_per_buffer=chunk_size)

        print(f"...开始录音，将持续{duration_sec}秒...")
        frames = []
        timestamp1 = int(time.time())

        for i in range(total_chunks):
            frame = stream.read(chunk_size, exception_on_overflow=False)
            frames.append(frame)

        #timestamp2 = int(time.time())
        print("...录音结束...")
        stream.stop_stream()
        stream.close()
        pa.terminate()
        print(frames)
        #dt = datetime.fromtimestamp(timestamp1)
        #formatted_time1 = dt.strftime("%Y-%m-%d %H:%M:%S")
        # dt = datetime.fromtimestamp(timestamp2)
        # formatted_time2 = dt.strftime("%Y-%m-%d %H:%M:%S")
        return b"".join(frames), timestamp1#formatted_time1, formatted_time2

    def get_speech_segments_with_embeddings(self, audio_bytes: bytes,time_start, **kwargs) -> List[Dict[str, Any]]:
        """
        处理音频字节流，返回每个语音片段的文本和声纹嵌入。
        """
        model = self.model
        if not model.vad_model:
            raise ValueError("AutoModel实例必须在初始化时包含VAD模型 (vad_model)。")
        if not model.spk_model:
            raise ValueError("AutoModel实例必须在初始化时包含声纹模型 (spk_model)。")

        print("开始推理处理...")

        print("1. 正在进行VAD切分...")
        vad_result = model.inference(
            input=audio_bytes,
            model=model.vad_model,
            kwargs=model.vad_kwargs,
            **kwargs
        )
        vad_segments = vad_result[0]['value']
        print("vad_result",vad_result)
        print(f"VAD检测到 {len(vad_segments)} 个片段。")

        if not vad_segments:
            print("未检测到有效语音片段。")
            return []

        speech_array = np.frombuffer(audio_bytes, dtype=np.int16)
        sample_rate = 16000
        processed_segments = []

        for i, (start_ms, end_ms) in enumerate(vad_segments):
            print(f"\n--- 正在处理片段 {i + 1}/{len(vad_segments)} ({start_ms}ms -> {end_ms}ms) ---")
            start_sample = int(start_ms * sample_rate / 1000)
            end_sample = int(end_ms * sample_rate / 1000)
            segment_audio_int16 = speech_array[start_sample:end_sample]

            if len(segment_audio_int16) == 0:
                print("片段为空，跳过。")
                continue
            print("   a. 正在进行语音识别 (ASR)...")
            segment_audio = (segment_audio_int16 / 32768.0).astype(np.float32)
            asr_result = model.inference(
                input=segment_audio,
                model=model.model,
                hotword=self.hotwords,  # 传入热词
                **kwargs
            )
            segment_text = asr_result[0]['text']

            print("   b. 正在提取声纹 (SPK)...")
            spk_result = model.inference(
                input=segment_audio,
                model=model.spk_model,
                kwargs=model.spk_kwargs,
                **kwargs
            )
            segment_embedding = spk_result[0]['spk_embedding']

            processed_segments.append({
                "text": segment_text,
                "embedding": segment_embedding,
                "time": [datetime.fromtimestamp(time_start+start_ms//1000.0).strftime("%Y-%m-%d %H:%M:%S"),datetime.fromtimestamp(time_start+end_ms//1000.0).strftime("%Y-%m-%d %H:%M:%S")]
            })

        print("\n所有片段处理完毕。")
        return processed_segments


if __name__ == '__main__':
    home_directory = os.path.expanduser("~")
    asr_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                                  "speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch")
    asr_model_revision = "v2.0.4"
    vad_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                                  "speech_fsmn_vad_zh-cn-16k-common-pytorch")
    vad_model_revision = "v2.0.4"
    punc_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                                   "punc_ct-transformer_zh-cn-common-vocab272727-pytorch")
    punc_model_revision = "v2.0.4"
    spk_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                                  "speech_campplus_sv_zh-cn_16k-common")
    spk_model_revision = "v2.0.4"
    hotword_file = "./hotwords.txt"
    ngpu = 1
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ncpu = psutil.cpu_count()

    # ASR 模型
    model = AutoModel(model=asr_model_path,
                      model_revision=asr_model_revision,
                      vad_model=vad_model_path,
                      vad_model_revision=vad_model_revision,
                      punc_model=punc_model_path,
                      punc_model_revision=punc_model_revision,
                      spk_model=spk_model_path,
                      spk_model_revision=spk_model_revision,
                      ngpu=ngpu,
                      ncpu=ncpu,
                      device=device,
                      disable_pbar=True,
                      disable_log=True,
                      disable_update=True
                      )
    try:
        # 1. 初始化处理类
        procedure = Procedure(model=model)
        #
        # # 2. 进入主循环
        # while True:
        # 3. 等待用户指令

        # 4. 从麦克风录制一句话,返回时间戳
        audio_data_bytes,t1 = procedure.record_duration_time()

        # 5. 调用模型进行推理
        results = procedure.get_speech_segments_with_embeddings(audio_data_bytes,t1)

        # 6. 打印结果
        print("\n\n" + "=" * 20 + " 推理结果 " + "=" * 20)
        # if results:
        #     for i, res in enumerate(results):
        #         print(f"片段 {i + 1}:")
        #         print(f"  识别文本: '{res['text']}'")
        #         print(f"  声纹嵌入形状: {res['embedding'].shape}")
        #         print(f"  声纹嵌入设备: {res['embedding'].device}")
        #         # 打印前5个维度的值，作为示例
        #         print(f"  声纹嵌入预览: {res['embedding'].flatten()[:5].tolist()}...")
        #         print(f"  语音时间,{res['time']}...")
        #         print("-" * 40)
        # else:
        #     print("没有识别到有效结果。")
        print(results)
        print("=" * 52 + "\n")

    except KeyboardInterrupt:
        print("\n程序已终止。")
    except Exception as e:
        print(f"\n发生错误: {e}")