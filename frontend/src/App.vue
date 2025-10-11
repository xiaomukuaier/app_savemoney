<template>
  <div id="app">
    <el-container class="app-container">
      <el-header class="app-header">
        <h1>SaveMoney 智能记账</h1>
        <p class="subtitle">语音输入，智能记账</p>
      </el-header>

      <el-main class="app-main">
        <AudioRecorder
          @audio-recorded="handleAudioRecorded"
          @recording-state-changed="handleRecordingStateChanged"
        />

        <ExpenseDisplay
          v-if="expenseData"
          :expense="expenseData"
          @confirm="handleConfirmExpense"
          @cancel="handleCancelExpense"
        />

        <div v-if="statusMessage" class="status-message">
          {{ statusMessage }}
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AudioRecorder from './components/AudioRecorder.vue'
import ExpenseDisplay from './components/ExpenseDisplay.vue'
import { submitAudio, confirmExpense } from './services/api'
import type { Expense } from './types/expense'

const expenseData = ref<Expense | null>(null)
const statusMessage = ref('')

const handleAudioRecorded = async (audioBlob: Blob) => {
  statusMessage.value = '正在处理语音...'

  try {
    const result = await submitAudio(audioBlob)
    expenseData.value = result.data
    statusMessage.value = '请确认记账信息'
  } catch (error) {
    statusMessage.value = '处理失败，请重试'
    console.error('Audio processing failed:', error)
  }
}

const handleRecordingStateChanged = (isRecording: boolean) => {
  statusMessage.value = isRecording ? '正在录音...' : ''
}

const handleConfirmExpense = async (expense: Expense) => {
  statusMessage.value = '正在保存...'

  try {
    await confirmExpense(expense)
    statusMessage.value = '记账成功！'
    expenseData.value = null

    // 3秒后清除状态消息
    setTimeout(() => {
      statusMessage.value = ''
    }, 3000)
  } catch (error) {
    statusMessage.value = '保存失败，请重试'
    console.error('Expense confirmation failed:', error)
  }
}

const handleCancelExpense = () => {
  expenseData.value = null
  statusMessage.value = '已取消'
}
</script>

<style scoped>
.app-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.app-header {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  text-align: center;
}

.app-header h1 {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 300;
}

.subtitle {
  margin: 8px 0 0 0;
  font-size: 1rem;
  opacity: 0.8;
}

.app-main {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 2rem;
}

.status-message {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: white;
  font-size: 0.9rem;
}
</style>