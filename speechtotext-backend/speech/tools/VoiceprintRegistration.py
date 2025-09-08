import os
from typing import Optional

import torch
import numpy as np
import sklearn.metrics.pairwise
import warnings
import ffmpeg

from funasr import AutoModel
import torch.nn.functional as F

warnings.filterwarnings("ignore")




class VoiceprintRegistration:
    def __init__(self, model: AutoModel,sr=16000):
        if not all(hasattr(model, attr) for attr in ['vad_model', 'spk_model', 'vad_kwargs', 'spk_kwargs']):
            raise ValueError("传入的AutoModel实例缺少必要的属性 (vad_model, spk_model, vad_kwargs, spk_kwargs)。")

        self.model = model
        self.device = model.kwargs.get("device", "cpu")
        # speakers 改成存储一个 list，每个说话人有多个 embedding
        self.speakers = {}
        self.sr = sr

    def _load_audio_as_bytes(self, filepath: str) -> Optional[bytes]:
        try:
            out_bytes, _ = (
                ffmpeg.input(filepath,threads=0, hwaccel='cuda')
                .output("-", format="wav", acodec="pcm_s16le", ac=1, ar=16000)
                .run(cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True)
            )
            return out_bytes
        except ffmpeg.Error as e:
            print(f"错误：使用 FFmpeg 加载音频文件 '{os.path.basename(filepath)}' 失败。")
            print(f"FFmpeg stderr: {e.stderr.decode(errors='ignore')}")
            return None

    def register(self, audio_input: str, text: str):
        print(f"--- 注册 '{text}', 音频: '{os.path.basename(audio_input)}' ---")

        audio_bytes = self._load_audio_as_bytes(audio_input)
        if audio_bytes is None:
            print(f"注册失败：音频加载失败。")
            return

        # vad_params = self.model.vad_kwargs.copy()
        # vad_params.pop('model', None)
        vad_result = self.model.inference(
            input=audio_bytes,
            model=self.model.vad_model,
            kwargs=self.model.vad_kwargs
        )

        if not vad_result or "value" not in vad_result[0] or not vad_result[0]["value"]:
            print(f"注册失败：未在音频中检测到有效语音。")
            return

        vad_segments = vad_result[0]["value"]
        speech_np = np.frombuffer(audio_bytes, np.int16).astype(np.float32) / 32768.0

        speech_segments = []
        for seg in vad_segments:
            start_ms, end_ms = seg
            start = int(start_ms / 1000 * self.sr)
            end = int(end_ms / 1000 * self.sr)
            if start < end <= len(speech_np):
                speech_segments.append(speech_np[start:end])

        if not speech_segments:
            print(f"注册失败：未能切分出有效语音片段。")
            return


        spk_results = self.model.inference(
            input=speech_segments,
            model=self.model.spk_model,
            kwargs=self.model.spk_kwargs
        )
        embeddings = [res["spk_embedding"] for res in spk_results if "spk_embedding" in res]

        if embeddings:
            valid_count = 0
            for emb in embeddings:
                if torch.isnan(emb).any():
                    print(f"警告：检测到 NaN embedding，已跳过。")
                    continue
                self.speakers.setdefault(text, []).append(emb.squeeze())
                valid_count += 1
            if valid_count > 0:
                print(f"成功！说话人 '{text}' 已注册 {valid_count} 个有效 embedding。")
            else:
                print(f"注册失败：所有 embedding 都无效。")
        else:
            print(f"注册失败：未能提取声纹特征。")

    def speech_to_speaker(self, audio_input: str, threshold: float = 0.6) -> str:
        if not self.speakers:
            print("识别错误：无已注册声纹。")
            return "未知说话人"

        print(f"--- 识别音频: '{os.path.basename(audio_input)}' ---")

        audio_bytes = self._load_audio_as_bytes(audio_input)
        if audio_bytes is None:
            return "未知说话人"

        vad_result = self.model.inference(
            input=audio_bytes,
            model=self.model.vad_model,
            kwargs=self.model.vad_kwargs
        )

        if not vad_result or "value" not in vad_result[0] or not vad_result[0]["value"]:
            return "未知说话人"

        vad_segments = vad_result[0]["value"]
        speech_np = np.frombuffer(audio_bytes, np.int16).astype(np.float32) / 32768.0

        speech_segments = []
        for seg in vad_segments:
            start_ms, end_ms = seg
            start = int(start_ms / 1000 * self.sr)
            end = int(end_ms / 1000 * self.sr)
            if start < end <= len(speech_np):
                speech_segments.append(speech_np[start:end])

        if not speech_segments:
            return "未知说话人"

        spk_results = self.model.inference(
            input=speech_segments,
            model=self.model.spk_model,
            kwargs=self.model.spk_kwargs
        )
        embeddings = [res["spk_embedding"] for res in spk_results if "spk_embedding" in res]

        if not embeddings:
            return "未知说话人"

        embeddings_tensor = torch.cat(embeddings, dim=0)
        input_embedding = torch.mean(embeddings_tensor, dim=0).squeeze()
        if torch.isnan(input_embedding).any():
            print("识别失败：输入 embedding 含 NaN。")
            return "未知说话人"
        input_embedding_np = input_embedding.cpu().numpy().reshape(1, -1)

        max_similarity = -1.0
        recognized_speaker = "未知说话人"

        for text, registered_embeddings in self.speakers.items():
            for reg_emb in registered_embeddings:
                if torch.isnan(reg_emb).any():
                    print(f"警告：跳过 NaN embedding (说话人 {text})")
                    continue
                reg_emb_np = reg_emb.cpu().numpy().reshape(1, -1)
                similarity = sklearn.metrics.pairwise.cosine_similarity(input_embedding_np, reg_emb_np)[0][0]
                print(f"与 '{text}' 的相似度: {similarity:.4f}")
                if similarity > max_similarity:
                    max_similarity = similarity
                    if max_similarity > threshold:
                        recognized_speaker = text

        print(f"最高相似度 {max_similarity:.4f} (阈值: {threshold})")
        return recognized_speaker

    # def embedding_to_speaker(self, input_embedding: torch.Tensor, threshold: float = 0.6) -> str:
    #     """
    #     输入已经提取好的 embedding，返回匹配的说话人
    #     """
    #     if not self.speakers:
    #         print("识别错误：无已注册声纹。")
    #         return "未知说话人"
    #
    #     if torch.isnan(input_embedding).any():
    #         print("识别失败：输入 embedding 含 NaN。")
    #         return "未知说话人"
    #
    #     input_embedding_np = input_embedding.detach().cpu().numpy().reshape(1, -1)
    #
    #     max_similarity = -1.0
    #     recognized_speaker = "未知说话人"
    #
    #     for text, registered_embeddings in self.speakers.items():
    #         for reg_emb in registered_embeddings:
    #             if torch.isnan(reg_emb).any():
    #                 print(f"警告：跳过 NaN embedding (说话人 {text})")
    #                 continue
    #             reg_emb_np = reg_emb.cpu().numpy().reshape(1, -1)
    #             similarity = sklearn.metrics.pairwise.cosine_similarity(input_embedding_np, reg_emb_np)[0][0]
    #             print(f"与 '{text}' 的相似度: {similarity:.4f}")
    #             if similarity > max_similarity:
    #                 max_similarity = similarity
    #                 if max_similarity > threshold:
    #                     recognized_speaker = text
    #
    #     print(f"最高相似度 {max_similarity:.4f} (阈值: {threshold})")
    #     return recognized_speaker
    def embedding_to_speaker(self, input_embedding: torch.Tensor) -> str:
        """
        输入已经提取好的 embedding，返回相似度最高的说话人
        """
        if not self.speakers:
            print("识别错误：无已注册声纹。")
            return "未知说话人"

        if torch.isnan(input_embedding).any():
            print("识别失败：输入 embedding 含 NaN。")
            return "未知说话人"

        input_embedding_np = input_embedding.detach().cpu().numpy().reshape(1, -1)

        max_similarity = -1.0
        recognized_speaker = "未知说话人"

        for speaker_name, registered_embeddings in self.speakers.items():
            for reg_emb in registered_embeddings:
                if torch.isnan(reg_emb).any():
                    print(f"警告：跳过 NaN embedding (说话人 {speaker_name})")
                    continue
                reg_emb_np = reg_emb.cpu().numpy().reshape(1, -1)
                similarity = sklearn.metrics.pairwise.cosine_similarity(input_embedding_np, reg_emb_np)[0][0]
                print(f"与 '{speaker_name}' 的相似度: {similarity:.4f}")
                if similarity > max_similarity:
                    max_similarity = similarity
                    recognized_speaker = speaker_name

        print(f"最高相似度 {max_similarity:.4f}")
        return recognized_speaker

    def bytes_to_speaker(self, audio_bytes: bytes, threshold: float = 0.6) -> str:
        """
        输入 audio_bytes，返回匹配的说话人
        """
        if not self.speakers:
            print("识别错误：无已注册声纹。")
            return "未知说话人"

        vad_result = self.model.inference(
            input=audio_bytes,
            model=self.model.vad_model,
            kwargs=self.model.vad_kwargs
        )

        if not vad_result or "value" not in vad_result[0] or not vad_result[0]["value"]:
            return "未知说话人"

        vad_segments = vad_result[0]["value"]
        speech_np = np.frombuffer(audio_bytes, np.int16).astype(np.float32) / 32768.0

        speech_segments = []
        for seg in vad_segments:
            start_ms, end_ms = seg
            start = int(start_ms / 1000 * self.sr)
            end = int(end_ms / 1000 * self.sr)
            if start < end <= len(speech_np):
                speech_segments.append(speech_np[start:end])

        if not speech_segments:
            return "未知说话人"

        spk_results = self.model.inference(
            input=speech_segments,
            model=self.model.spk_model,
            kwargs=self.model.spk_kwargs
        )
        embeddings = [res["spk_embedding"] for res in spk_results if "spk_embedding" in res]

        if not embeddings:
            return "未知说话人"

        embeddings_tensor = torch.cat(embeddings, dim=0)
        input_embedding = torch.mean(embeddings_tensor, dim=0).squeeze()

        return self.embedding_to_speaker(input_embedding)

# ===================================================================
#                      主函数 (您的代码保持不变)
# ===================================================================
if __name__ == '__main__':
    # ... 您的主函数代码无需任何修改 ...
    audio_file_zhangsan_1 = "2025-09-01/output/0/1.mp3"
    audio_file_zhangsan_2 = "2025-09-01/output/0/2.mp3"
    audio_file_zhangsan_3 = "2025-09-01/output/0/3.mp3"
    audio_file_zhangsan_4 = "2025-09-01/output/0/4.mp3"
    audio_file_zhangsan_5 = "2025-09-01/output/0/5.mp3"
    audio_file_zhangsan_6 = "2025-09-01/output/0/6.mp3"
    audio_file_lisi_1 = "2025-09-01/output/1/30.mp3"
    audio_file_lisi_2 = "2025-09-01/output/1/31.mp3"
    audio_file_lisi_3 = "2025-09-01/output/1/32.mp3"
    audio_file_lisi_4 = "2025-09-01/output/1/33.mp3"
    audio_file_lisi_5 = "2025-09-01/output/1/34.mp3"
    audio_file_unknown = "2025-09-01/output/2/8.mp3"

    if not all(os.path.exists(f) for f in
               [audio_file_zhangsan_1, audio_file_zhangsan_2, audio_file_lisi_1, audio_file_unknown]):
        print("错误：请确保音频文件存在于您的项目中，或修改为正确的路径。")
    else:
        home_directory = os.path.expanduser("~")
        asr_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                                      "speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch")
        vad_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                                      "speech_fsmn_vad_zh-cn-16k-common-pytorch")
        punc_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                                       "punc_ct-transformer_zh-cn-common-vocab272727-pytorch")
        spk_model_path = os.path.join(home_directory, ".cache", "modelscope", "hub", "models", "iic",
                                      "speech_campplus_sv_zh-cn_16k-common")
        device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"正在使用设备: {device}")
        print("正在初始化FunASR AutoModel...")

        model = AutoModel(model=asr_model_path,
                          vad_model=vad_model_path,
                          punc_model=punc_model_path,
                          spk_model=spk_model_path,
                          device=device,
                          disable_pbar=True,
                          disable_log=True,
                          disable_update=True
                          )
        print("模型初始化完成。")

        registration_system = VoiceprintRegistration(model=model)

        print("\n" + "=" * 25 + " 开始注册 " + "=" * 25)
        registration_system.register(audio_file_zhangsan_1, "说话人1")
        registration_system.register(audio_file_zhangsan_2, "说话人1")
        registration_system.register(audio_file_zhangsan_3, "说话人1")
        registration_system.register(audio_file_zhangsan_4, "说话人1")
        registration_system.register(audio_file_zhangsan_5, "说话人1")
        registration_system.register(audio_file_lisi_1, "说话人2")
        registration_system.register(audio_file_lisi_2, "说话人2")
        registration_system.register(audio_file_lisi_3, "说话人2")
        registration_system.register(audio_file_lisi_4, "说话人2")
        print(registration_system.speakers)
        print("\n" + "=" * 25 + " 开始识别 " + "=" * 25)
        speaker1 = registration_system.speech_to_speaker(audio_file_zhangsan_6)
        print(f"--> 识别结果: 音频 '{os.path.basename(audio_file_zhangsan_2)}' 的说话人是: 【{speaker1}】\n")

        speaker2 = registration_system.speech_to_speaker(audio_file_lisi_5)
        print(f"--> 识别结果: 音频 '{os.path.basename(audio_file_lisi_5)}' 的说话人是: 【{speaker2}】\n")

        speaker3 = registration_system.speech_to_speaker(audio_file_unknown)
        print(f"--> 识别结果: 音频 '{os.path.basename(audio_file_unknown)}' 的说话人是: 【{speaker3}】\n")