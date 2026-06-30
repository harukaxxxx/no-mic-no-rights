<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">管理音效</h1>

    <UploadArea @files="handleFiles" class="mb-8" />

    <div v-if="uploading" class="mb-4 text-blue-400">上傳中...</div>

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
      <div class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2">
        <ManageCard
          v-for="sound in pinnedSounds"
          :key="sound.id"
          :sound="sound"
          :is-previewing="store.previewingId === sound.id"
          @preview="store.startPreview(sound)"
          @update="updateSound"
          @delete="deleteSound"
        />
      </div>
    </div>

    <div>
      <h2 class="text-xl font-bold mb-4">所有音效</h2>
      <div class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2">
        <ManageCard
          v-for="sound in sortedSounds"
          :key="sound.id"
          :sound="sound"
          :is-previewing="store.previewingId === sound.id"
          @preview="store.startPreview(sound)"
          @update="updateSound"
          @delete="deleteSound"
        />
      </div>
    </div>

    <div v-if="duplicateInfo" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div class="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h2 class="text-lg font-bold mb-4">發現重複音效</h2>
        <p class="text-gray-300 mb-2">
          「{{ duplicateInfo.newFileName }}」與已有的「{{ duplicateInfo.existingSound.name }}」內容相同。
        </p>
        <p class="text-gray-400 text-sm mb-6">要覆蓋現有的音效嗎？</p>
        <div class="flex justify-end gap-3">
          <button
            @click="skipDuplicate"
            class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
          >
            跳過
          </button>
          <button
            @click="confirmOverwrite"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded transition-colors"
          >
            覆蓋
          </button>
        </div>
      </div>
    </div>

    <NowPlaying :current-playing="store.currentPlaying" :error="store.error" :success="store.success" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSoundsStore, Sound } from '../stores/sounds'
import UploadArea from '../components/UploadArea.vue'
import ManageCard from '../components/ManageCard.vue'
import NowPlaying from '../components/NowPlaying.vue'

const store = useSoundsStore()
const uploading = ref(false)
const search = ref('')
const sortBy = ref('created_at')
const duplicateInfo = ref<{ newFileName: string; existingSound: Sound; fileHash: string } | null>(null)
const pendingFiles = ref<File[]>([])

const pinnedSounds = computed(() =>
  filteredSounds.value.filter(s => s.is_pinned)
)

const sortedSounds = computed(() =>
  filteredSounds.value.filter(s => !s.is_pinned)
)

const filteredSounds = computed(() => {
  let result = store.sounds
  if (search.value) {
    result = result.filter(s =>
      s.name.toLowerCase().includes(search.value.toLowerCase()) ||
      s.tags.toLowerCase().includes(search.value.toLowerCase())
    )
  }
  if (sortBy.value === 'name') {
    result = [...result].sort((a, b) => a.name.localeCompare(b.name))
  } else if (sortBy.value === 'play_count') {
    result = [...result].sort((a, b) => b.play_count - a.play_count)
  } else {
    result = [...result].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  }
  return result
})

async function handleFiles(files: FileList) {
  uploading.value = true
  const fileArray = Array.from(files)
  pendingFiles.value = []

  try {
    for (const file of fileArray) {
      const name = file.name.replace(/\.[^/.]+$/, "")
      const result = await store.uploadSound(file, name)

      if (result.duplicate && result.existing_sound && result.file_hash) {
        duplicateInfo.value = {
          newFileName: name,
          existingSound: result.existing_sound,
          fileHash: result.file_hash
        }
        pendingFiles.value = fileArray.slice(fileArray.indexOf(file) + 1)
        return
      }

      store.showSuccess(`「${name}」上傳成功`)
    }
  } finally {
    uploading.value = false
  }
}

async function confirmOverwrite() {
  if (!duplicateInfo.value) return

  const name = duplicateInfo.value.existingSound.name
  uploading.value = true
  try {
    await store.overwriteSound(duplicateInfo.value.fileHash)
  } finally {
    uploading.value = false
  }

  duplicateInfo.value = null
  store.showSuccess(`「${name}」已覆蓋`)
  await continuePendingFiles()
}

function skipDuplicate() {
  duplicateInfo.value = null
  continuePendingFiles()
}

async function continuePendingFiles() {
  if (pendingFiles.value.length === 0) return

  uploading.value = true
  try {
    for (const file of pendingFiles.value) {
      const name = file.name.replace(/\.[^/.]+$/, "")
      const result = await store.uploadSound(file, name)

      if (result.duplicate && result.existing_sound && result.file_hash) {
        duplicateInfo.value = {
          newFileName: name,
          existingSound: result.existing_sound,
          fileHash: result.file_hash
        }
        pendingFiles.value = pendingFiles.value.slice(pendingFiles.value.indexOf(file) + 1)
        return
      }

      store.showSuccess(`「${name}」上傳成功`)
    }
  } finally {
    uploading.value = false
    pendingFiles.value = []
  }
}

async function updateSound(sound: Sound) {
  await store.updateSound(sound.id, {
    name: sound.name,
    is_pinned: sound.is_pinned,
    volume: sound.volume,
  })
}

async function deleteSound(id: number) {
  if (confirm('確定要刪除這個音效嗎？')) {
    store.stopPreview()
    await store.deleteSound(id)
  }
}

onMounted(() => {
  store.fetchSounds()
})
</script>
