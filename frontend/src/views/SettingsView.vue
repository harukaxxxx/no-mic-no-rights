<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">設定</h1>
    
    <div class="space-y-6 max-w-2xl">
      <div>
        <label class="block text-sm font-medium mb-2">跟隨的 Discord User ID</label>
        <input 
          v-model="followUserId"
          @blur="saveSetting('follow_user_id', followUserId)"
          type="text"
          placeholder="例如：123456789012345678"
          class="w-full bg-gray-800 border border-gray-700 rounded px-4 py-2"
        />
        <p class="mt-1 text-sm text-gray-400">Bot 會自動跟隨此使用者進出語音頻道</p>
      </div>

      <div>
        <label class="block text-sm font-medium mb-2">Bot Token</label>
        <input 
          v-model="botToken"
          @blur="saveSetting('discord_bot_token', botToken)"
          type="password"
          placeholder="your_bot_token"
          class="w-full bg-gray-800 border border-gray-700 rounded px-4 py-2"
        />
      </div>

      <div class="bg-gray-800 rounded-lg p-4">
        <h2 class="font-medium mb-2">Bot 狀態</h2>
        <p class="text-gray-400">Bot 目前{{ botConnected ? '已' : '未' }}連線</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const followUserId = ref('')
const botToken = ref('')
const botConnected = ref(false)

async function loadSettings() {
  try {
    const response = await axios.get('/api/settings')
    const settings = response.data
    followUserId.value = settings.follow_user_id || ''
    botToken.value = settings.discord_bot_token || ''
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}

async function saveSetting(key: string, value: string) {
  try {
    await axios.put(`/api/settings/${key}`, null, { params: { value } })
  } catch (error) {
    console.error('Failed to save setting:', error)
  }
}

onMounted(() => {
  loadSettings()
})
</script>
