<template>
  <div class="rounded-lg overflow-hidden flex flex-col border border-gray-600/50">
    <div
      class="relative aspect-[2/1] cursor-pointer hover:ring-2 hover:ring-blue-500 transition-all"
      :style="{ background: gradient }"
      :class="{ 'ring-2 ring-blue-500': isPreviewing }"
      @click="$emit('preview')"
    >
      <img
        v-if="sound.cover_image"
        :src="`/api/sounds/${sound.id}/cover`"
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full flex items-center justify-center p-3 text-center">
        <span class="text-base font-semibold text-white drop-shadow-md">{{ sound.name }}</span>
      </div>

      <div v-if="sound.is_pinned" class="absolute top-1.5 left-1.5 text-yellow-400 text-sm">
        📌
      </div>

      <div v-if="isPreviewing" class="absolute inset-0 bg-black/40 flex items-center justify-center">
        <span class="text-white text-2xl animate-pulse">▶</span>
      </div>
    </div>

    <div class="p-2 flex flex-col gap-1.5 bg-gray-800">
      <input
        v-model="sound.name"
        @blur="$emit('update', sound)"
        placeholder="名稱"
        class="bg-transparent border-b border-gray-600 focus:border-blue-500 outline-none text-sm font-medium"
      />

      <div class="flex items-center gap-1.5">
        <span class="text-sm text-gray-500">🔊</span>
        <input
          type="range"
          min="0"
          max="200"
          :value="Math.round((sound.volume ?? 1) * 100)"
          @input="updateVolume"
          @change="$emit('update', sound)"
          class="flex-1 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
        />
        <span class="text-sm text-gray-500 w-8 text-right">{{ Math.round((sound.volume ?? 1) * 100) }}%</span>
      </div>

      <div class="flex items-center justify-between pt-0.5">
        <label class="flex items-center gap-1 cursor-pointer">
          <input
            type="checkbox"
            v-model="sound.is_pinned"
            @change="$emit('update', sound)"
            class="w-3 h-3"
          />
          <span class="text-sm text-gray-400">釘選</span>
        </label>

        <button
          @click="$emit('delete', sound.id)"
          class="text-red-500 hover:text-red-400 text-sm"
        >
          刪除
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Sound } from '../stores/sounds'

const props = defineProps<{
  sound: Sound
  isPreviewing: boolean
}>()

function updateVolume(e: Event) {
  const target = e.target as HTMLInputElement
  props.sound.volume = Number(target.value) / 100
}

function hashToHSL(seed: number, offset: number) {
  const h = ((seed * 137.508 + offset * 60) % 360)
  const s = 30 + ((seed * 13 + offset * 37) % 20)
  const l = 15 + ((seed * 7 + offset * 23) % 12)
  return [h, s, l]
}

const gradient = computed(() => {
  const [h1, s1, l1] = hashToHSL(props.sound.id, 0)
  const [h2, s2, l2] = hashToHSL(props.sound.id, 1)
  const angle = (props.sound.id * 47) % 360
  return `linear-gradient(${angle}deg, hsl(${h1}, ${s1}%, ${l1}%), hsl(${h2}, ${s2}%, ${l2}%))`
})

defineEmits<{
  preview: []
  update: [sound: Sound]
  delete: [id: number]
}>()
</script>
