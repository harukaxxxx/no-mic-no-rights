<template>
  <div v-if="currentPlaying" class="fixed bottom-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg">
    <div class="flex items-center gap-2">
      <span class="animate-pulse">▶</span>
      <span>{{ currentPlaying.name }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Sound } from '../stores/sounds'

defineProps<{
  currentPlaying: Sound | null
}>()
</script>
