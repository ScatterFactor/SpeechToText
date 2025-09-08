<template>
    <div class="meeting-recorder">
        <header class="header">
            <div class="logo">
                <i class="fas fa-microphone"></i>
                <h1>会议语音记录与总结系统</h1>
            </div>
            <!-- <div class="user-actions">
                <button class="btn btn-secondary" @click="showSettings = !showSettings">
                    <i class="fas fa-cog"></i> 设置
                </button>
            </div> -->
        </header>

        <div class="main-content">
            <div class="card transcription-panel">
                <div class="panel-header">
                    <h2 class="panel-title">实时会议记录</h2>
                    <div class="recording-status" v-if="isRecording">
                        <div class="recording-indicator"></div>
                        <span>正在录制中 - {{ formatTime(recordingTime) }}</span>
                    </div>
                </div>

                <div class="transcription-content">
                    <div v-for="(speaker, index) in speakers" :key="index"
                        :class="['speaker', `speaker-${speaker.id}`]">
                        <div class="speaker-header">
                            <div class="speaker-icon">S{{ speaker.id }}</div>
                            <strong>{{ speaker.speaker }}</strong>
                            <span class="time">{{ speaker.time }}</span>
                        </div>
                        <div class="speaker-text">
                            {{ speaker.text }}
                        </div>
                    </div>
                </div>

                <div class="controls">
                    <!-- <button class="btn btn-primary" @click="startRecording">
                        <i class="fas fa-play"></i> {{ pauseRecording_ ? '新记录' : '开始记录' }}
                    </button> -->
                    <button class="btn btn-primary" @click="startNewRecording()">
                        <i class="fas fa-play"></i> 新记录
                    </button>
                    <button class="btn btn-secondary" @click="pauseRecording" :disabled="!isRecording">
                        <i class="fas fa-pause"></i> 暂停记录
                    </button>
                    <button class="btn btn-primary" @click="startRecording" v-if="!isRecording && pauseRecording_">
                        <i class="fas fa-pause"></i> 继续记录
                    </button>
                    <button class="btn btn-success" @click="saveRecording">
                        <i class="fas fa-save"></i> 保存记录
                    </button>
                </div>
            </div>

            <div class="card summary-panel">
                <div class="panel-header">
                    <h2 class="panel-title">会议摘要</h2>
                    <button class="btn btn-primary" @click="generateSummary">
                        <i class="fas fa-sync"></i> 生成摘要
                    </button>
                </div>

                <div class="summary-content">
                    <div class="summary-point">
                        {{ summaryPoints }}
                    </div>
                </div>
            </div>

            <!-- <div class="card summary-panel">
                <div class="panel-header">
                    <h2 class="panel-title">会议摘要</h2>
                    <button class="btn btn-primary" @click="generateSummary">
                        <i class="fas fa-sync"></i> 生成摘要
                    </button>
                </div>


                <div class="summary-content">
                    <div class="summary-point">
                        {{ summaryPoints }}
                    </div>
                </div>

            </div> -->
        </div>

        <div class="management-panel">
            <!-- <div class="card">
                <div class="panel-header">
                    <h2 class="panel-title">会议记录管理</h2>
                </div>

                <ul class="file-list">
                    <li v-for="(file, index) in savedFiles" :key="index" class="file-item">
                        <div class="file-name">
                            <i class="fas fa-file-audio"></i> {{ file.title }}
                        </div>
                        <div class="file-actions">
                            <button class="btn-icon" @click="viewMeetingHistory(file)" title="查看">
                                <i class="fas fa-eye"></i>查看
                            </button>
                            <button class="btn-icon" @click="deleteMeetingHistory(file, index)" title="删除">
                                <i class="fas fa-trash"></i>删除
                            </button>
                        </div>
                    </li>
                </ul>
            </div> -->

            <div class="card">
                <div class="panel-header">
                    <h2 class="panel-title">会议记录管理</h2>
                </div>

                <ul class="file-list">
                    <li v-for="(file, index) in savedFiles" :key="index" class="file-item">
                        <div class="file-name">
                            <i class="fas fa-file-audio"></i> {{ file.title }}
                        </div>
                        <div class="file-actions">
                            <button class="btn-view" @click="viewMeetingHistory(file)" title="查看">
                                <i class="fas fa-eye">查看</i>
                                <!-- <span>查看</span> -->
                            </button>
                            <button class="btn-delete" @click="deleteMeetingHistory(file, index)" title="删除">
                                <i class="fas fa-trash">删除</i>
                                <!-- <span>删除</span> -->
                            </button>
                        </div>
                    </li>
                </ul>
            </div>

            <div class="card settings-panel" v-if="showSettings">
                <div class="panel-header">
                    <h2 class="panel-title">识别设置</h2>
                </div>

                <div class="setting-item">
                    <label class="setting-label">语音识别模型</label>
                    <select class="setting-select" v-model="settings.model">
                        <option value="standard">标准模型（推荐）</option>
                        <option value="meeting">会议优化模型</option>
                        <option value="high-accuracy">高精度模型（速度较慢）</option>
                    </select>
                </div>

                <div class="setting-item">
                    <label class="setting-label">发言人识别</label>
                    <select class="setting-select" v-model="settings.speakerRecognition">
                        <option value="auto">自动识别不同发言人</option>
                        <option value="manual">手动设置发言人</option>
                        <option value="off">关闭发言人识别</option>
                    </select>
                </div>

                <div class="setting-item">
                    <label class="setting-label">摘要生成长度</label>
                    <select class="setting-select" v-model="settings.summaryLength">
                        <option value="short">简洁（3-5点）</option>
                        <option value="medium">标准（5-7点）</option>
                        <option value="long">详细（7-10点）</option>
                    </select>
                </div>

                <div class="controls">
                    <button class="btn btn-primary" @click="saveSettings">
                        <i class="fas fa-save"></i> 保存设置
                    </button>
                </div>
            </div>
        </div>

        <div class="voiceprint-panel">
            <div class="card">
                <div class="panel-header">
                    <h2 class="panel-title">声纹管理</h2>
                    <button class="btn btn-primary" @click="showVoiceprintForm = !showVoiceprintForm">
                        <i class="fas fa-plus"></i> 添加声纹
                    </button>
                </div>

                <!-- 声纹添加表单 -->
                <div class="voiceprint-form" v-if="showVoiceprintForm">
                    <div class="form-group">
                        <label class="form-label">说话人姓名</label>
                        <input type="text" class="form-input" v-model="newVoiceprint.speakerName" placeholder="输入说话人姓名">
                    </div>
                    <div class="form-group">
                        <label class="form-label">上传音频文件</label>
                        <div class="file-upload-area" @click="triggerFileUpload" @drop.prevent="handleFileDrop"
                            @dragover.prevent @dragenter.prevent>
                            <i class="fas fa-cloud-upload-alt"></i>
                            <p>拖放音频文件到这里或点击选择文件</p>
                            <input type="file" ref="fileInput" @change="handleFileSelect" accept="audio/*" hidden>
                            <p class="file-name" v-if="newVoiceprint.file">{{ newVoiceprint.file.name }}</p>
                        </div>
                    </div>
                    <div class="form-actions">
                        <button class="btn btn-secondary" @click="cancelVoiceprintAdd">取消</button>
                        <button class="btn btn-primary" @click="addVoiceprint"
                            :disabled="!isVoiceprintValid">添加</button>
                    </div>
                </div>

                <!-- 声纹列表 -->
                <div class="voiceprint-list">
                    <div v-for="(voiceprint, index) in voiceprints" :key="index" class="voiceprint-item">
                        <div class="voiceprint-info">
                            <div class="speaker-avatar">
                                <!-- {{ getInitials(voiceprint.speakerName) }} -->
                                {{ getInitials(voiceprint.speaker_name) }}
                            </div>
                            <div class="voiceprint-details">
                                <!-- <h4>{{ voiceprint.speakerName }}</h4>
                                <p>{{ voiceprint.fileName }}</p> -->
                                <h4>{{ voiceprint.speaker_name }}</h4>
                                <p>{{ voiceprint.audio_filename }}</p>
                                <span class="upload-date">添加于: {{ voiceprint.upload_date }}</span>
                                <!-- <span class="upload-date">添加于: {{ voiceprint.uploadDate }}</span> -->
                                <!-- <span class="upload-date">添加于: {{ voiceprint.timeStamp }}</span> -->
                            </div>
                        </div>
                        <div class="voiceprint-actions">
                            <button class="btn-delete" @click="deleteVoiceprint(index, voiceprint.id)">
                                <i class="fas fa-trash"></i>
                                <span>删除</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 输入会议主题模态框 -->
        <div class="modal" v-if="showSaveModal" key="save-modal">
            <div class="modal-content">
                <h3>保存会议记录</h3>
                <p>请输入会议主题：</p>
                <input type="text" v-model="meetingTopic" placeholder="例如：产品需求讨论会">
                <div class="modal-actions">
                    <button class="btn btn-secondary" @click="cancelSaveRecording">取消</button>
                    <button class="btn btn-primary" @click="confirmSaveRecording">确定</button>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
export default {
    name: 'MeetingRecorder',
    data() {
        return {
            //服务器基础路由
            baseURL: process.env.VUE_APP_API_BASE,
            isRecording: false,
            newRecording_: true,
            pauseRecording_: false,
            recordingTime: 0,
            showSettings: false,
            recordingInterval: null,
            recordingStartTime: 0, // 新增：记录开始录制的时间戳

            //语音转文字变量
            speakers: [],
            //会议总结变量
            summaryPoints: "",
            //会议列表变量
            savedFiles: [],
            settings: {
                model: 'standard',
                speakerRecognition: 'auto',
                summaryLength: 'medium'
            },
            showVoiceprintForm: false,
            newVoiceprint: {
                speakerName: '',
                file: null
            },
            voiceprints: [],

            //麦克风相关数据
            audioContext: null,
            mediaRecorder: null,
            audioChunks: [],
            audioStream: null,
            isRecordingAudio: false,
            recordedAudio: null,
            recognition: null, // 语音识别对象
            recognitionText: '', // 当前识别的文本

            //会议主题相关变量
            showSaveModal: false, // 新增：控制保存模态框显示
            meetingTopic: '',     // 新增：用户输入的会议主题

            //websocket相关变量
            ws: null,
            isWsConnected: false,
            wsReconnectAttempts: 0,
            maxReconnectAttempts: 5

        }
    },

    created() {
        this.getAllMeetingRecorder();
        this.getAllVoicePrints();
    },

    computed: {
        isVoiceprintValid() {
            return this.newVoiceprint.speakerName.trim() !== '' && this.newVoiceprint.file !== null;
        }
    },
    methods: {

        startNewRecording() {
            this.newRecording_ = true;
            this.startRecording();
        },

        //获取所有会议主题列表
        getAllMeetingRecorder() {
            fetch(`${this.baseURL}/speech/meetings/`, {
                method: 'GET'
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error("获取会议记录失败");
                    }
                    return response.json();
                })
                .then(data => {
                    //假设数据中含有meetingTopics字段
                    // this.savedFiles = data.meetingTopics;
                    this.savedFiles = data;
                    console.log("获取的会议列表", this.savedFiles)
                })
                .catch(error => {
                    console.log(error);
                })
        },

        //查看某条会议记录
        viewMeetingHistory(file) {
            // 会议ID
            this.speakers = [];
            this.speakers = file.transcription;
            this.summaryPoints = file.summary;
        },

        deleteMeetingHistory(file, index) {
            const meetingId = file.id;
            fetch(`${this.baseURL}/speech/meetings/${meetingId}/`, {
                method: 'DELETE'
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`删除 ${file.name} 失败！`);
                    }
                    return;
                })
                .then(data => {
                    alert("删除成功！")
                    this.savedFiles.splice(index, 1);
                    data;
                })
                .catch(error => {
                    console.log(error);
                })
        },

        getAllVoicePrints() {
            fetch(`${this.baseURL}/speech/voiceprints/`, {
                method: "GET"
            })
                .then(response => {
                    console.log(response)
                    if (!response.ok) {
                        throw new Error("获取声纹数据失败");
                    }
                    return response.json();
                })
                .then(data => {
                    console.log(data)
                    this.voiceprints = data;
                    let i = 0;
                    for (i = 0; i < this.voiceprints.length; i++) {
                        //格式化时间
                        this.voiceprints[i].upload_date = new Date(this.voiceprints[i].upload_date).toLocaleString('zh-CN', {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit',
                            hour12: false // 使用24小时制
                        });
                    }
                })
                .catch(error => {
                    console.log('获取所有声纹列表失败:' + error);
                    // alert('获取所有声纹数据失败');
                })
        },

        uploadAudio(audioData) {
            console.log('将一秒的音频文件上传给后端');
            // console.log(audioData);
            // this.speakers[this.speakers.length - 1].text += '这是一秒的识别内容 \n';
            const formData = new FormData();
            formData.append('audio', audioData);
            formData.append('timestamp', Date.now());
            fetch(`${this.baseURL}/api/upLoadAudio`, {
                method: 'POST',
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('上传失败');
                    }
                    return response.json()
                })
                .then(data => {
                    if (data.success) {
                        console.log('音频上传成功');
                        //加入data中有{speaker:说话人, text: 语音识别的内容, time: 后端接收前端音频数据的时间}
                        //获得最近一次的说话人
                        const theLastSpeaker = this.speakers[this.speakers.length - 1].name;
                        const theCurrSpeaker = data.speaker;
                        if (theCurrSpeaker === theLastSpeaker) {
                            this.speakers[this.speakers.length - 1].text += data.text;
                        }
                        else {
                            this.speakers.push({ name: data.name, time: data.time, text: data.text });
                        }

                    }
                })
                .catch(error => {
                    console.log('语音识别失败：' + error);
                })
        },


        mergeBuffers(bufferQueue) {
            const length = bufferQueue.reduce((sum, buf) => sum + buf.length, 0);
            const result = new Float32Array(length);
            let offset = 0;
            for (const buf of bufferQueue) {
                result.set(buf, offset);
                offset += buf.length;
            }
            return result;
        },

        convertFloat32ToInt16(buffer) {
            const l = buffer.length;
            const buf = new Int16Array(l);
            for (let i = 0; i < l; i++) {
                let s = Math.max(-1, Math.min(1, buffer[i]));
                buf[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
            }
            return buf;
        },
        async startRecording() {
            if (this.newRecording_) {
                this.speakers = [];
                this.summaryPoints = "";
                this.recordingTime = 0;
                this.newRecording_ = false;
                this.isRecording = false;
            }
            if (this.isRecording) return;

            try {
                //新记录，将内容清空
                if (this.newRecording_) {
                    this.speakers = [];
                    this.isRecording = true;
                    this.pauseRecording_ = false;
                    this.summaryPoints = "";
                    this.recordingTime = 0;
                    this.newRecording_ = false;
                }
                // if (!this.isRecording && this.newRecording_) {
                //     this.speakers = [];
                //     this.isRecording = true;
                //     this.pauseRecording_ = false;
                //     this.summaryPoints = "";
                //     this.recordingTime = 0;
                //     this.newRecording_ = false;
                // }

                this.isRecording = true;
                this.pauseRecording_ = false;
                this.newRecording_ = false;
                // this.speakers = [];
                this.isRecording = true;
                this.bufferedPCM = [];
                this.bufferedTime = 0;

                // 记录开始时间
                this.recordingStartTime = Date.now() - (this.recordingTime || 0) * 1000;

                // 启动计时器
                this.recordingInterval = setInterval(() => {
                    const elapsed = Date.now() - this.recordingStartTime;
                    this.recordingTime = Math.round(elapsed / 1000);
                }, 100);

                // 获取麦克风权限
                this.stream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        sampleRate: 16000,
                        channelCount: 1,
                        echoCancellation: true,
                        noiseSuppression: true
                    },
                    video: false
                });

                // 创建 AudioContext
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                    sampleRate: 16000
                });

                const source = this.audioContext.createMediaStreamSource(this.stream);

                // ScriptProcessorNode 处理音频帧
                const processor = this.audioContext.createScriptProcessor(4096, 1, 1);
                source.connect(processor);
                processor.connect(this.audioContext.destination);

                processor.onaudioprocess = (e) => {
                    const inputData = e.inputBuffer.getChannelData(0); // Float32 [-1,1]
                    const pcm16 = this.convertFloat32ToInt16(inputData);

                    // 缓存 PCM16
                    this.bufferedPCM.push(pcm16);
                    this.bufferedTime += inputData.length / 16000; // 秒数

                    // 如果累计到 5 秒就发送
                    if (this.bufferedTime >= 3) {
                        this.sendBufferedAudio();
                        this.bufferedPCM = [];
                        this.bufferedTime = 0;
                    }
                };

                this.processor = processor;

            } catch (error) {
                console.error("启动录音失败:", error);
                this.isRecording = false;
            }
        },

        // 发送缓存 PCM16 给后端
        sendBufferedAudio() {
            if (!this.bufferedPCM.length) return;

            // 合并所有 Float32 -> Int16 的块
            let totalLength = this.bufferedPCM.reduce((sum, arr) => sum + arr.length, 0);
            let merged = new Int16Array(totalLength);
            let offset = 0;
            this.bufferedPCM.forEach(arr => {
                merged.set(arr, offset);
                offset += arr.length;
            });

            // 发送给后端
            const blob = new Blob([merged.buffer], { type: 'application/octet-stream' });
            const formData = new FormData();
            formData.append('audio', blob, 'audio.pcm');
            // 新建控制器，每次调用 fetch 时都可取消
            this.abortController = new AbortController();

            fetch('http://127.0.0.1:8000/speech/recognize/', {
                method: 'POST',
                body: formData,
                signal: this.abortController.signal
            }).then(res => res.json())
                .then(data => {
                    console.log("识别结果:", data);
                    console.log("识别结果数据类型:", typeof data);
                    console.log("识别结果对象的属性:", Object.keys(data));

                    let speech_result = data.results;
                    console.log('data.result的内容：', data.results);
                    console.log('speech_result的数据类型：', speech_result instanceof Array);

                    let i = 0;
                    for (i = 0; i < speech_result.length; i++) {

                        let theLastSpeaker = (this.speakers.length > 0) ? this.speakers[this.speakers.length - 1].speaker : '';
                        let theCurrSpeaker = speech_result[i].speaker;
                        if (theLastSpeaker === theCurrSpeaker) {
                            this.speakers[this.speakers.length - 1].text += " " + speech_result[i].text;
                        }
                        else {
                            this.speakers.push({ speaker: theCurrSpeaker, text: speech_result[i].text, time: speech_result[i].time[0] });
                        }
                    }
                })
                .catch(err => console.error(err));
        },


        async pauseRecording() {
            if (!this.isRecording) return;

            // 1. 停止计时器
            this.pauseRecording_ = true;
            this.newRecording_ = false;
            this.isRecording = false;
            if (this.recordingInterval) {
                clearInterval(this.recordingInterval);
                this.recordingInterval = null;
            }

            // 2. 停止音频处理节点
            if (this.processor) {
                this.processor.disconnect();
                this.processor.onaudioprocess = null;
            }

            // 3. 关闭音频流
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
            }

            // 4. 关闭 AudioContext
            if (this.audioContext) {
                await this.audioContext.close();
            }


            fetch(`${this.baseURL}/speech/refine/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'applicatoin/json'
                },
                body: JSON.stringify(this.speakers)

            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('优化对话失败');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('优化后的对话内容：', data);
                    this.speakers = data;
                })
                .catch(error => {
                    console.log('优化对话失败：', error);
                })

            // 5. 如果有残留音频数据（未满5秒），也要发送一次
            if (this.bufferedPCM && this.bufferedPCM.length > 0) {
                this.sendBufferedAudio();
                this.bufferedPCM = [];
                this.bufferedTime = 0;
            }



            // 6. 如果有挂起的 fetch，取消
            if (this.abortController) {
                this.abortController.abort();
                this.abortController = null;
            }

            this.isRecording = false;
            console.log("录音已停止");
        },

        // pauseRecording() {
        //     this.pauseRecording_ = true;
        //     this.isRecording = false;
        //     if (this.recordingInterval) {
        //         clearInterval(this.recordingInterval);
        //         this.recordingInterval = null;
        //     }
        //     // 停止录音
        //     if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
        //         this.mediaRecorder.stop();
        //     }

        //     // 关闭麦克风
        //     this.stopMicrophone();
        // },

        //关闭麦克风
        stopMicrophone() {
            if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                this.mediaRecorder.stop();
                console.log('停止录音');
            }

            //关闭麦克风
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
                this.stream = null;
                console.log('麦克风流已停止');
            }
            // if (this.audioStream) {
            //     // 停止所有轨道
            //     this.audioStream.getTracks().forEach(track => {
            //         try {
            //             track.stop(); // 停止轨道
            //             track.enabled = false; // 禁用轨道
            //         } catch (error) {
            //             console.error('停止轨道失败:', error);
            //         }
            //     });

            //     // 释放资源
            //     this.audioStream = null;
            // }

            // 重置媒体录制器
            if (this.mediaRecorder) {
                this.mediaRecorder = null;
            }

            console.log('麦克风已关闭');
        },
        saveRecording() {
            // 在实际应用中，这里会保存录音和转录文本
            this.isRecording = false;
            this.pauseRecording_ = false;

            // 重置计时相关状态
            if (this.recordingInterval) {
                clearInterval(this.recordingInterval);
                this.recordingInterval = null;
            }
            this.recordingTime = 0;          // 重置计时为0
            this.recordingStartTime = null;   // 清除开始时间戳
            this.pauseRecording_ = false;     // 重置暂停状态

            if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                this.mediaRecorder.stop();
            }

            // 关闭麦克风
            this.stopMicrophone();
            // 显示保存模态框
            this.showSaveModal = true;
            console.log('showSaveModal：', this.showSaveModal);

            // alert('会议记录已保存！');

            // 添加到已保存文件列表
            // const date = new Date();
            // const fileName = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}_会议记录`;
            // this.savedFiles.unshift({ name: fileName });
        },

        //输入会议主题相关函数

        confirmSaveRecording() {

            fetch(`${this.baseURL}/speech/meetings/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: this.meetingTopic,
                    transcription: this.speakers,
                    summary: this.summaryPoints
                })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('保存失败')
                    }
                    return;
                })
                .then(data => {
                    // 假设data中含有success字段
                    // if (data.success) {
                    //     alert('会议记录已保存！');
                    //     this.meetingTopic = '';
                    //     this.showSaveModal = false;
                    //     this.speakers = [];
                    //     this.summaryPoints = [];
                    //     // 重新获得所有会议记录主题列表
                    //     this.getAllMeetingRecorder();
                    // }
                    alert('会议记录已保存！');
                    this.meetingTopic = '';
                    this.showSaveModal = false;
                    this.getAllMeetingRecorder();
                    data;
                })
                .catch(error => {
                    console.log('保存会议记录失败：' + error);
                    this.showSaveModal = false;
                });

            // this.showSaveModal = false;

        },

        cancelSaveRecording() {
            // 重置会议主题并关闭模态框
            this.meetingTopic = '';
            this.showSaveModal = false;
            console.log('会议模态框关闭');
        },

        generateSummary() {
            // 在实际应用中，这里会调用AI生成摘要
            let meetingContent = '';
            let i = 0;
            while (i < this.speakers.length) {
                meetingContent += this.speakers[i].speaker + '：' + this.speakers[i].text + '\n';
                i += 1;
            }
            this.summaryPoints = "AI摘要生成中..."
            fetch(`${this.baseURL}/speech/summarize/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: meetingContent
                })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('AI会议总结生成失败');
                    }
                    return response.json();
                })
                .then(data => {
                    this.summaryPoints = data.summary;
                })
                .catch(error => {
                    console.log(error);
                })
            // alert('正在生成会议摘要...')
        },
        exportSummary() {
            alert('导出会议摘要功能')
        },
        downloadFile(file) {
            alert(`下载: ${file.name}`)
        },
        // deleteMeetingHistory(index) {
        //     if (confirm('确定要删除这个文件吗？')) {
        //         this.savedFiles.splice(index, 1)
        //     }
        // },
        saveSettings() {
            alert('设置已保存')
            this.showSettings = false
        },
        formatTime(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        },
        triggerFileUpload() {
            this.$refs.fileInput.click();
        },

        handleFileSelect(event) {
            const file = event.target.files[0];
            if (file && file.type.startsWith('audio/')) {
                this.newVoiceprint.file = file;
            } else {
                alert('请选择有效的音频文件');
            }
        },

        handleFileDrop(event) {
            const files = event.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type.startsWith('audio/')) {
                    this.newVoiceprint.file = file;
                } else {
                    alert('请拖放有效的音频文件');
                }
            }
        },

        addVoiceprint() {
            if (this.isVoiceprintValid) {

                //这里用于静态页面展示
                let newVoiceprintTimeStamp = Date.now();
                this.voiceprints.unshift({
                    speakerName: this.newVoiceprint.speakerName,
                    fileName: this.newVoiceprint.file.name,
                    uploadDate: new Date().toLocaleString('zh-CN', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                        hour12: false // 使用24小时制
                    }),
                    timeStamp: newVoiceprintTimeStamp
                });

                // 在实际应用中，这里应该上传文件到服务器
                // alert(`已添加 ${this.newVoiceprint.speakerName} 的声纹`);

                const formData = new FormData();
                formData.append('speaker_name', this.newVoiceprint.speakerName);
                formData.append('audio_filename', this.newVoiceprint.file.name);
                formData.append('audio_file', this.newVoiceprint.file);
                // formData.append('timesStamp', newVoiceprintTimeStamp);

                fetch(`${this.baseURL}/speech/voiceprints/`, {
                    method: 'POST',
                    body: formData
                })
                    .then(response => { response; return; })
                    .then(data => {
                        // 处理响应...
                        // response的结构：{"success":true, "message":"声纹添加成功"}
                        this.getAllVoicePrints();
                        //后端添加成功，同时更新前端声纹列表
                        // this.voiceprints.unshift({
                        //     speakerName: this.newVoiceprint.speakerName,
                        //     fileName: this.newVoiceprint.file.name,
                        //     uploadDate: new Date().toLocaleString('zh-CN', {
                        //         year: 'numeric',
                        //         month: '2-digit',
                        //         day: '2-digit',
                        //         hour: '2-digit',
                        //         minute: '2-digit',
                        //         second: '2-digit',
                        //         hour12: false // 使用24小时制
                        //     }),
                        //     timeStamp: newVoiceprintTimeStamp
                        // });
                        alert(`声纹添加成功`);
                        data;
                    })
                    .catch(error => {
                        // 错误处理...
                        alert('声纹添加失败');
                        console.log(error);
                    });

                // 重置表单
                this.cancelVoiceprintAdd();
            }
        },

        cancelVoiceprintAdd() {
            this.newVoiceprint = {
                speakerName: '',
                file: null
            };
            this.showVoiceprintForm = false;
        },

        deleteVoiceprint(index, id) {
            if (confirm('确定要删除这个声纹吗？')) {
                // this.voiceprints.splice(index, 1);
                fetch(`${this.baseURL}/speech/voiceprints/${id}/`, {
                    method: 'DELETE',
                })
                    .then(response => {
                        response;
                        return;
                    })
                    .then(data => {
                        data;
                        alert("声纹删除成功");
                        this.getAllVoicePrints();
                    })
                    .catch(error => {
                        alert("声纹删除失败");
                        console.log(error);
                    })
            }
        },

        getInitials(name) {
            return name ? name.charAt(0) : '?';
        }
    },
    beforeDestroy() {
        if (this.recordingInterval) {
            clearInterval(this.recordingInterval)
        }
    },

}
</script>

<style scoped>
.meeting-recorder {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
    color: white;
    border-radius: 10px 10px 0 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.logo {
    display: flex;
    align-items: center;
    gap: 10px;
}

.logo i {
    font-size: 24px;
}

.main-content {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
    margin-top: 20px;
}

.card {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.transcription-panel {
    min-height: 400px;
}

.summary-panel {
    min-height: 400px;
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.panel-title {
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
}

.transcription-content {
    height: 300px;
    overflow-y: auto;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 15px;
}

.speaker {
    margin-bottom: 15px;
    padding: 10px;
    border-radius: 8px;
    background: white;
    box-shadow: 极 2px 5px rgba(0, 0, 0, 0.05);
}


.speaker-header {
    display: flex;
    align-items: center;
    justify-content: center;
    /* 新增：水平居中 */
    gap: 10px;
    margin-bottom: 5px;
    position: relative;
    /* 新增：为绝对定位做准备 */
}

.speaker-icon {
    position: absolute;
    /* 新增：绝对定位 */
    left: 0;
    /* 新增：固定在左侧 */
    /* 其他原有样式保持不变 */
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
}

.speaker-text {
    text-align: left;
}


.speaker-1 .speaker-icon {
    background-color: #6a11cb;
}

.speaker-2 .speaker-icon {
    background-color: #2575fc;
}

.speaker-3 .speaker-icon {
    background-color: #ff6b6b;
}

.summary-content {
    padding: 15px;
    background: #e3f2fd;
    border-radius: 8px;
    margin-bottom: 15px;
    min-height: 250极;
}

.summary-point {
    margin-bottom: 10px;
    padding-left: 20px;
    position: relative;
}

.summary-point:before {
    content: "•";
    position: absolute;
    left: 0;
    color: #2575fc;
    font-size: 20px;
}

.controls {
    display: flex;
    gap: 10px;
    margin-top: 20px;
}

.btn {
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s ease;
}

.btn-primary {
    background: #2575fc;
    color: white;
}

.btn-primary:hover {
    background: #1a6be0;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background: #5a6268;
}

.btn-success {
    background: #28a745;
    color: white;
}

.btn-success:hover {
    background: #218838;
}

.management-panel {
    margin-top: 20px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.file-list {
    list-style: none;
    margin-top: 10px;
}

.file-item {
    padding: 10px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.file-actions {
    display: flex;
    gap: 10px;
}

.file-action {
    color: #2575fc;
    cursor: pointer;
}

.recording-status {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    background: #fff4e5;
    border-radius: 8px;
    margin-bottom: 15px;
}

.recording-indicator {
    width: 12px;
    height: 12px;
    background: #ff6b6b;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% {
        opacity: 1;
    }

    50% {
        opacity: 0.4;
    }

    100% {
        opacity: 1;
    }
}

.settings-panel {
    margin-top: 20px;
}

.setting-item {
    margin-bottom: 15px;
}

.setting-label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
}

.setting-select {
    width: 100%;
    padding: 8px;
    border-radius: 5极;
    border: 1px solid #ddd;
}

@media (max-width: 768px) {
    .main-content {
        grid-template-columns: 1fr;
    }

    .management-panel {
        grid-template-columns: 1fr;
    }

    .header {
        flex-direction: column;
        gap: 10px;
    }

    .controls {
        flex-direction: column;
    }
}

.voiceprint-panel {
    margin-top: 20px;
}

.voiceprint-form {
    padding: 20px;
    border: 1px solid #eee;
    border-radius: 8px;
    margin-bottom: 20px;
    background-color: #f9f9f9;
}

.form-group {
    margin-bottom: 15px;
}

.form-label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
    color: #333;
}

.form-input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 14px;
}

.file-upload-area {
    border: 2px dashed #ccc;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
}

.file-upload-area:hover {
    border-color: #2575fc;
    background-color: #f0f7ff;
}

.file-upload-area i {
    font-size: 48px;
    color: #2575fc;
    margin-bottom: 10px;
}

.file-upload-area p {
    margin: 5px 0;
    color: #666;
}

.file-name {
    font-weight: 500;
    color: #333;
    margin-top: 10px;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

.voiceprint-list {
    margin-top: 20px;
}

.voiceprint-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    border-bottom: 1px solid #eee;
    transition: background-color 0.2s;
}

.voiceprint-item:hover {
    background-color: #f9f9f9;
}

.voiceprint-info {
    display: flex;
    align-items: center;
    gap: 15px;
}

.speaker-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 18px;
}

.voiceprint-details h4 {
    margin: 0 0 5px 0;
    color: #333;
}

.voiceprint-details p {
    margin: 0 0 5px 0;
    color: #666;
}

.upload-date {
    font-size: 12px;
    color: #999;
}

.voiceprint-actions {
    display: flex;
    gap: 10px;
}

.btn-icon {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background-color: #f0f0f0;
    color: #666;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.btn-icon:hover {
    background-color: #2575fc;
    color: white;
}

.modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    padding: 20px;
    border-radius: 10px;
    width: 400px;
    max-width: 80%;
}

.modal-content h3 {
    margin-top: 0;
    color: #2c3e50;
}

.modal-content input {
    width: 100%;
    padding: 10px;
    margin: 10px 0;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 16px;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

.file-actions {
    display: flex;
    gap: 10px;
}

.btn-view,
.btn-delete {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.btn-view {
    background-color: #e3f2fd;
    color: #1a73e8;
}

.btn-view:hover {
    background-color: #d0e4fc;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(26, 115, 232, 0.2);
}

.btn-delete {
    background-color: #ffebee;
    color: #e53935;
}

.btn-delete:hover {
    background-color: #ffcdd2;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(229, 57, 53, 0.2);
}

.file-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 15px;
    border-bottom: 1px solid #f0f0f0;
    transition: background-color 0.3s;
}

.file-item:hover {
    background-color: #f9f9f9;
}

.file-name {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 16px;
}

.file-name i {
    color: #6a11cb;
}

.panel-title {
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
}

/* 会议记录管理按钮样式 - 修复水平排列 */
.file-actions .btn-view,
.file-actions .btn-delete,
.voiceprint-actions .btn-delete {
    display: inline-flex;
    flex-direction: row;
    /* 确保水平排列 */
    align-items: center;
    justify-content: center;
    padding: 8px 16px;
    /* 增加水平内边距 */
    border-radius: 20px;
    gap: 8px;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
    font-size: 14px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    width: auto;
    /* 移除固定宽度 */
    height: auto;
    /* 移除固定高度 */
}

.file-actions .btn-view {
    background-color: #e3f2fd;
    color: #1a73e8;
}

.file-actions .btn-delete,
.voiceprint-actions .btn-delete {
    background-color: #ffebee;
    color: #e53935;
}

.file-actions .btn-view:hover {
    background-color: #d0e4fc;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(26, 115, 232, 0.2);
}

.file-actions .btn-delete:hover,
.voiceprint-actions .btn-delete:hover {
    background-color: #ffcdd2;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(229, 57, 53, 0.2);
}

/* 确保图标和文字水平排列 */
.file-actions .btn-view i,
.file-actions .btn-delete i,
.voiceprint-actions .btn-delete i {
    display: inline;
    /* 确保图标是内联元素 */
    margin: 0;
    /* 移除外边距 */
}

/* 确保文件操作区域横向排列 */
.file-actions {
    display: flex;
    gap: 10px;
}

.summary-content {
    height: 300px;
    overflow-y: auto;
    padding: 15px;
    background: #e3f2fd;
    border-radius: 8px;
    margin-bottom: 15px;
    word-wrap: break-word;
    white-space: pre-wrap;
    text-align: left;
}
</style>