<template>
  <div class="audio-recorder">
    <el-button
      :type="isRecording ? 'danger' : 'primary'"
      :icon="isRecording ? 'VideoPause' : 'Microphone'"
      :loading="isProcessing"
      size="large"
      circle
      class="record-button"
      @mousedown="startRecording"
      @mouseup="stopRecording"
      @touchstart="startRecording"
      @touchend="stopRecording"
    >
      {{ isRecording ? '停止录音' : '按住录音' }}
    </el-button>

    <div v-if="isRecording" class="recording-indicator">
      <div class="pulse"></div>
      <span>正在录音...</span>
    </div>

    <div v-if="recordingTime > 0" class="recording-time">
      录音时长: {{ formatTime(recordingTime) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  'audio-recorded': [audioBlob: Blob]
  'recording-state-changed': [isRecording: boolean]
}>()

const isRecording = ref(false)
const isProcessing = ref(false)
const recordingTime = ref(0)
const mediaRecorder = ref<MediaRecorder | null>(null)
const audioChunks = ref<Blob[]>([])
let timer: number | null = null

const startRecording = async () => {
  if (isRecording.value) return

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    // 检查浏览器支持的音频格式
    let mimeType = 'audio/webm'
    if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
      mimeType = 'audio/webm;codecs=opus'
    } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
      mimeType = 'audio/mp4'
    } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
      mimeType = 'audio/ogg;codecs=opus'
    }

    console.log('使用音频格式:', mimeType)
    mediaRecorder.value = new MediaRecorder(stream, { mimeType })
    audioChunks.value = []

    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data)
      }
    }

    mediaRecorder.value.onstop = () => {
      const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' })
      emit('audio-recorded', audioBlob)

      // 停止所有音轨
      stream.getTracks().forEach(track => track.stop())
    }

    mediaRecorder.value.start()
    isRecording.value = true
    recordingTime.value = 0
    emit('recording-state-changed', true)

    // 开始计时
    timer = window.setInterval(() => {
      recordingTime.value++
    }, 1000)

  } catch (error) {
    console.error('Failed to start recording:', error)
    alert('无法访问麦克风，请检查权限设置')
  }
}

const stopRecording = () => {
  if (!isRecording.value || !mediaRecorder.value) return

  mediaRecorder.value.stop()
  isRecording.value = false
  emit('recording-state-changed', false)

  if (timer) {
    clearInterval(timer)
    timer = null
  }

  // 如果录音时间太短，不处理
  if (recordingTime.value < 1) {
    recordingTime.value = 0
    return
  }
}

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.audio-recorder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.record-button {
  width: 80px;
  height: 80px;
  font-size: 1.2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.record-button:hover {
  transform: scale(1.05);
}

.recording-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  font-size: 0.9rem;
}

.pulse {
  width: 12px;
  height: 12px;
  background-color: #ff4d4f;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
  100% {
    transform: scale(0.8);
    opacity: 1;
  }
}

.recording-time {
  color: white;
  font-size: 0.9rem;
  opacity: 0.8;
}
</style>