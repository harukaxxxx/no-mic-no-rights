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
  is_pinned: boolean
  play_count: number
  volume: number
  file_hash: string | null
  created_at: string
}

export interface UploadResult {
  duplicate?: boolean
  existing_sound?: Sound
  file_hash?: string
  id?: number
}

export const useSoundsStore = defineStore('sounds', () => {
  const sounds = ref<Sound[]>([])
  const loading = ref(false)
  const currentPlaying = ref<Sound | null>(null)
  const error = ref<string | null>(null)
  const success = ref<string | null>(null)
  const previewingId = ref<number | null>(null)
  let previewAudio: HTMLAudioElement | null = null

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
      error.value = null
    } catch (err: any) {
      error.value = err.response?.data?.detail || '播放失敗'
      setTimeout(() => { error.value = null }, 3000)
    }
  }

  async function uploadSound(file: File, name: string, category: string = '', tags: string = ''): Promise<UploadResult> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('name', name)
    formData.append('category', category)
    formData.append('tags', tags)
    
    try {
      const response = await axios.post('/api/sounds', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      if (!response.data.duplicate) {
        sounds.value.push(response.data)
      }
      return response.data
    } catch (error) {
      console.error('Failed to upload sound:', error)
      throw error
    }
  }

  async function overwriteSound(fileHash: string): Promise<Sound> {
    const formData = new FormData()
    formData.append('file_hash', fileHash)
    
    try {
      const response = await axios.post('/api/sounds/overwrite', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const index = sounds.value.findIndex(s => s.id === response.data.id)
      if (index !== -1) {
        sounds.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('Failed to overwrite sound:', error)
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

  function showSuccess(message: string) {
    success.value = message
    setTimeout(() => { success.value = null }, 3000)
  }

  function startPreview(sound: Sound) {
    if (previewAudio) {
      previewAudio.pause()
      previewAudio = null
    }
    
    if (previewingId.value === sound.id) {
      previewingId.value = null
      return
    }
    
    previewAudio = new Audio(`/api/sounds/${sound.id}/preview`)
    previewAudio.volume = Math.min(sound.volume ?? 1, 1)
    previewAudio.onended = () => { previewingId.value = null }
    previewAudio.onerror = () => { previewingId.value = null }
    previewAudio.play()
    previewingId.value = sound.id
  }

  function stopPreview() {
    if (previewAudio) {
      previewAudio.pause()
      previewAudio = null
    }
    previewingId.value = null
  }

  return {
    sounds,
    loading,
    currentPlaying,
    error,
    success,
    previewingId,
    fetchSounds,
    playSound,
    uploadSound,
    overwriteSound,
    updateSound,
    deleteSound,
    showSuccess,
    startPreview,
    stopPreview,
  }
})
