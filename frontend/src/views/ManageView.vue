<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">管理音效</h1>
    
    <UploadArea @files="handleFiles" class="mb-8" />

    <div v-if="uploading" class="mb-4 text-blue-400">上傳中...</div>

    <div class="space-y-4">
      <div 
        v-for="sound in store.sounds" 
        :key="sound.id"
        class="bg-gray-800 rounded-lg p-4 flex items-center gap-4"
      >
        <div class="flex-1">
          <input 
            v-model="sound.name"
            @blur="updateSound(sound)"
            class="bg-transparent border-b border-gray-600 focus:border-blue-500 outline-none"
          />
          <div class="flex gap-2 mt-2 text-sm text-gray-400">
            <input 
              v-model="sound.category"
              @blur="updateSound(sound)"
              placeholder="分類"
              class="bg-transparent border-b border-gray-600 focus:border-blue-500 outline-none"
            />
            <input 
              v-model="sound.shortcut_key"
              @blur="updateSound(sound)"
              placeholder="快捷鍵"
              class="bg-transparent border-b border-gray-600 focus:border-blue-500 outline-none w-20"
            />
          </div>
        </div>
        
        <label class="flex items-center gap-2">
          <input 
            type="checkbox" 
            v-model="sound.is_pinned"
            @change="updateSound(sound)"
          />
          <span class="text-sm">釘選</span>
        </label>
        
        <button 
          @click="deleteSound(sound.id)"
          class="text-red-500 hover:text-red-400"
        >
          刪除
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSoundsStore, Sound } from '../stores/sounds'
import UploadArea from '../components/UploadArea.vue'

const store = useSoundsStore()
const uploading = ref(false)

async function handleFiles(files: FileList) {
  uploading.value = true
  try {
    for (const file of Array.from(files)) {
      const name = file.name.replace(/\.[^/.]+$/, "")
      await store.uploadSound(file, name)
    }
  } finally {
    uploading.value = false
  }
}

async function updateSound(sound: Sound) {
  await store.updateSound(sound.id, {
    name: sound.name,
    category: sound.category,
    shortcut_key: sound.shortcut_key,
    is_pinned: sound.is_pinned,
  })
}

async function deleteSound(id: number) {
  if (confirm('確定要刪除這個音效嗎？')) {
    await store.deleteSound(id)
  }
}

onMounted(() => {
  store.fetchSounds()
})
</script>
