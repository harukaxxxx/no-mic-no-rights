<template>
  <div
    class="relative aspect-square rounded-lg overflow-hidden cursor-pointer border border-gray-600/50 hover:ring-2 hover:ring-blue-500 transition-all"
    :style="{ background: gradient }"
    @click="$emit('play', sound)"
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
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Sound } from '../stores/sounds'

const props = defineProps<{
  sound: Sound
}>()

defineEmits<{
  play: [sound: Sound]
}>()

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
</script>
