<template>
  <div>
    <div class="mb-6 flex gap-4">
      <input 
        v-model="search" 
        type="text" 
        placeholder="搜尋音效..." 
        class="flex-1 bg-gray-800 border border-gray-700 rounded px-4 py-2"
      />
      <select v-model="sortBy" class="bg-gray-800 border border-gray-700 rounded px-4 py-2">
        <option value="created_at">最新上傳</option>
        <option value="name">名稱</option>
        <option value="play_count">最常使用</option>
      </select>
    </div>

    <div v-if="pinnedSounds.length" class="mb-8">
      <h2 class="text-xl font-bold mb-4">釘選音效</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <SoundCard 
          v-for="sound in pinnedSounds" 
          :key="sound.id" 
          :sound="sound" 
          @play="playSound"
        />
      </div>
    </div>

    <div>
      <h2 class="text-xl font-bold mb-4">所有音效</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <SoundCard 
          v-for="sound in filteredSounds" 
          :key="sound.id" 
          :sound="sound" 
          @play="playSound"
        />
      </div>
    </div>

    <NowPlaying :current-playing="store.currentPlaying" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useSoundsStore, Sound } from '../stores/sounds'
import SoundCard from '../components/SoundCard.vue'
import NowPlaying from '../components/NowPlaying.vue'

const store = useSoundsStore()
const search = ref('')
const sortBy = ref('created_at')

const pinnedSounds = computed(() => 
  store.sounds.filter(s => s.is_pinned)
)

const filteredSounds = computed(() => {
  let result = store.sounds.filter(s => !s.is_pinned)
  
  if (search.value) {
    result = result.filter(s => 
      s.name.toLowerCase().includes(search.value.toLowerCase()) ||
      s.tags.toLowerCase().includes(search.value.toLowerCase())
    )
  }
  
  if (sortBy.value === 'name') {
    result.sort((a, b) => a.name.localeCompare(b.name))
  } else if (sortBy.value === 'play_count') {
    result.sort((a, b) => b.play_count - a.play_count)
  } else {
    result.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  }
  
  return result
})

function playSound(sound: Sound) {
  store.playSound(sound)
}

function handleKeydown(e: KeyboardEvent) {
  if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
    return
  }
  
  const key = e.key.toLowerCase()
  const sound = store.sounds.find(s => s.shortcut_key?.toLowerCase() === key)
  if (sound) {
    playSound(sound)
  }
}

onMounted(() => {
  store.fetchSounds()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>
