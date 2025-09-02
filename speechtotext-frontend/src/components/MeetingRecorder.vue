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
                            <strong>{{ speaker.name }}</strong>
                            <span class="time">{{ speaker.time }}</span>
                        </div>
                        <div class="speaker-text">
                            {{ speaker.text }}
                        </div>
                    </div>
                </div>

                <div class="controls">
                    <button class="btn btn-primary" @click="startRecording">
                        <i class="fas fa-play"></i> {{ pauseRecording_ ? '继续记录' : '开始记录' }}
                    </button>
                    <button class="btn btn-secondary" @click="pauseRecording" :disabled="!isRecording">
                        <i class="fas fa-pause"></i> 暂停记录
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
                        <i class="fas fa-sync"></i> 重新生成
                    </button>
                </div>

                <div class="summary-content">
                    <div v-for="(point, index) in summaryPoints" :key="index" class="summary-point">
                        {{ point }}
                    </div>
                </div>

                <div class="controls">
                    <button class="btn btn-primary" @click="exportSummary">
                        <i class="fas fa-file-export"></i> 导出摘要
                    </button>
                    <!-- <button class="btn btn-secondary" @click="copySummary">
                        <i class="fas fa-copy"></i> 复制到剪贴板
                    </button> -->
                </div>
            </div>
        </div>

        <div class="management-panel">
            <div class="card">
                <div class="panel-header">
                    <h2 class="panel-title">会议记录管理</h2>
                </div>

                <ul class="file-list">
                    <li v-for="(file, index) in savedFiles" :key="index" class="file-item">
                        <div class="file-name">
                            <i class="fas fa-file-audio"></i> {{ file.name }}
                        </div>
                        <div class="file-actions">
                            <button class="btn-icon" @click="viewMeetingHistory(file)" title="查看">
                                <i class="fas fa-eye"></i>查看
                            </button>
                            <button class="btn-icon" @click="deleteMeetingHistory(index)" title="删除">
                                <i class="fas fa-trash"></i>删除
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
                                {{ getInitials(voiceprint.speakerName) }}
                            </div>
                            <div class="voiceprint-details">
                                <h4>{{ voiceprint.speakerName }}</h4>
                                <p>{{ voiceprint.fileName }}</p>
                                <span class="upload-date">添加于: {{ voiceprint.uploadDate }}</span>
                            </div>
                        </div>
                        <div class="voiceprint-actions">
                            <button class="btn-icon" @click="deleteVoiceprint(index)">
                                <span><i class="fas fa-trash"></i>删除</span>
                            </button>
                        </div>
                    </div>
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
            isRecording: false,
            pauseRecording_: false,
            recordingTime: 0,
            showSettings: false,
            recordingInterval: null,
            recordingStartTime: 0, // 新增：记录开始录制的时间戳
            speakers: [
                {
                    id: 1,
                    name: '发言人 1',
                    time: '10:05 AM',
                    text: '大家好，欢迎参加今天的项目会议。我们今天主要讨论Q2季度产品开发进度和下一步计划。'
                },
                {
                    id: 2,
                    name: '发言人 2',
                    time: '10:07 AM',
                    text: '目前前端开发已完成80%，后端API开发进度稍慢，大约完成65%。我们需要在下周中期进行第一次集成测试。'
                },
                {
                    id: 3,
                    name: '发言人 3',
                    time: '10:12 AM',
                    text: '关于数据库优化部分，我建议采用读写分离的方案，这可以提高系统在高并发情况下的性能表现。'
                }
            ],
            summaryPoints: [
                '讨论了Q2季度产品开发进度，前端完成80%，后端完成65%',
                '计划下周中期进行第一次集成测试',
                '提出了数据库读写分离的优化方案以提高高并发性能',
                '要求准备详细技术方案在下次会议讨论',
                '需要确认测试团队是否提前介入'
            ],
            savedFiles: [
                { name: '2023-09-15_产品会议记录' },
                { name: '2023-09-10_技术讨论记录' },
                { name: '2023-09-05_项目启动会议' }
            ],
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
            voiceprints: [
                // {
                //     speakerName: '张三',
                //     fileName: 'zhangsan_voice.mp3',
                //     uploadDate: '2023-09-20'
                // },
                // {
                //     speakerName: '李四',
                //     fileName: 'lisi_voice.wav',
                //     uploadDate: '2023-09-19'
                // }
            ]

        }
    },
    computed: {
        isVoiceprintValid() {
            return this.newVoiceprint.speakerName.trim() !== '' && this.newVoiceprint.file !== null;
        }
    },
    methods: {
        startRecording() {
            if (!this.isRecording) {
                this.isRecording = true;

                // 记录开始时间
                this.recordingStartTime = Date.now() - this.recordingTime * 1000;

                // 使用更精确的计时方法
                this.recordingInterval = setInterval(() => {
                    // 计算经过的时间（毫秒）
                    const elapsed = Date.now() - this.recordingStartTime;
                    // 转换为秒并四舍五入
                    this.recordingTime = Math.round(elapsed / 1000);
                }, 100); // 每100毫秒更新一次，更平滑
            }
        },
        pauseRecording() {
            this.pauseRecording_ = true;
            this.isRecording = false;
            if (this.recordingInterval) {
                clearInterval(this.recordingInterval);
                this.recordingInterval = null;
            }
        },
        saveRecording() {
            // 在实际应用中，这里会保存录音和转录文本
            this.isRecording = false;

            // 重置计时相关状态
            if (this.recordingInterval) {
                clearInterval(this.recordingInterval);
                this.recordingInterval = null;
            }
            this.recordingTime = 0;          // 重置计时为0
            this.recordingStartTime = null;   // 清除开始时间戳
            this.pauseRecording_ = false;     // 重置暂停状态

            alert('会议记录已保存！');

            // 添加到已保存文件列表
            const date = new Date();
            const fileName = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}_会议记录`;
            this.savedFiles.unshift({ name: fileName });
        },
        generateSummary() {
            // 在实际应用中，这里会调用AI生成摘要
            alert('正在生成会议摘要...')
        },
        exportSummary() {
            alert('导出会议摘要功能')
        },
        downloadFile(file) {
            alert(`下载: ${file.name}`)
        },
        deleteMeetingHistory(index) {
            if (confirm('确定要删除这个文件吗？')) {
                this.savedFiles.splice(index, 1)
            }
        },
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
                this.voiceprints.unshift({
                    speakerName: this.newVoiceprint.speakerName,
                    fileName: this.newVoiceprint.file.name,
                    uploadDate: new Date().toLocaleDateString()
                });

                // 在实际应用中，这里应该上传文件到服务器
                alert(`已添加 ${this.newVoiceprint.speakerName} 的声纹`);

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

        deleteVoiceprint(index) {
            if (confirm('确定要删除这个声纹吗？')) {
                this.voiceprints.splice(index, 1);
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

.s极aker-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 5px;
}

.speaker-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
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
</style>