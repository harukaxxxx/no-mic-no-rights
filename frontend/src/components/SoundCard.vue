<template>
  <div 
    class="relative aspect-square bg-gray-800 rounded-lg overflow-hidden cursor-pointer hover:ring-2 hover:ring-blue-500 transition-all"
    @click="$emit('play', sound)"
  >
    <img 
      v-if="sound.cover_image" 
      :src="`/api/sounds/${sound.id}/cover`" 
      class="w-full h-full object-cover"
    />
    <div 
      v-else 
      class="w-full h-full flex items-center justify-center p-4 text-center"
    >
      <span class="text-lg font-medium">{{ sound.name }}</span>
    </div>
    
    <div v-if="sound.shortcut_key" class="absolute top-2 right-2 bg-black/70 px-2 py-1 rounded text-xs">
      {{ sound.shortcut_key }}
    </div>
    
    <div v-if="sound.is_pinned" class="absolute top-2 left-2 text-yellow-400">
      📌
    </div>
  </div>
</template>

<script setup lang="ts">
import { Sound } from '../stores/sounds'

defineProps<{
  sound: Sound
}>()

defineEmits<{
  play: [sound: Sound]
}>()
</script>
