import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export interface Sound {
  id: number
  name: string
  filename: string
  category: string
  tags: string
  cover_image: string | null
  shortcut_key: string | null
  is_pinned: boolean
  play_count: number
  created_at: string
}

export const useSoundsStore = defineStore('sounds', () => {
  const sounds = ref<Sound[]>([])
  const loading = ref(false)
  const currentPlaying = ref<Sound | null>(null)

  async function fetchSounds() {
    loading.value = true
    try {
      const response = await axios.get('/api/sounds')
      sounds.value = response.data
    } catch (error) {
      console.error('Failed to fetch sounds:', error)
    } finally {
      loading.value = false
    }
  }

  async function playSound(sound: Sound) {
    try {
      await axios.post(`/api/sounds/${sound.id}/play`)
      currentPlaying.value = sound
      sound.play_count++
    } catch (error) {
      console.error('Failed to play sound:', error)
      alert('播放失敗：' + (error.response?.data?.detail || '未知錯誤'))
    }
  }

  async function uploadSound(file: File, name: string, category: string = '', tags: string = '') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('name', name)
    formData.append('category', category)
    formData.append('tags', tags)
    
    try {
      const response = await axios.post('/api/sounds', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      sounds.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('Failed to upload sound:', error)
      throw error
    }
  }

  async function updateSound(id: number, data: Partial<Sound>) {
    try {
      const response = await axios.put(`/api/sounds/${id}`, null, { params: data })
      const index = sounds.value.findIndex(s => s.id === id)
      if (index !== -1) {
        sounds.value[index] = { ...sounds.value[index], ...data }
      }
      return response.data
    } catch (error) {
      console.error('Failed to update sound:', error)
      throw error
    }
  }

  async function deleteSound(id: number) {
    try {
      await axios.delete(`/api/sounds/${id}`)
      sounds.value = sounds.value.filter(s => s.id !== id)
    } catch (error) {
      console.error('Failed to delete sound:', error)
      throw error
    }
  }

  return {
    sounds,
    loading,
    currentPlaying,
    fetchSounds,
    playSound,
    uploadSound,
    updateSound,
    deleteSound,
  }
})
