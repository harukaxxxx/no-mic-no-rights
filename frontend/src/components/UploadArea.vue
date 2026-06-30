<template>
  <div 
    class="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-blue-500 transition-colors"
    @dragover.prevent
    @drop.prevent="handleDrop"
  >
    <input 
      ref="fileInput"
      type="file" 
      multiple 
      accept="audio/*" 
      class="hidden"
      @change="handleFileSelect"
    />
    <button 
      @click="($refs.fileInput as HTMLInputElement).click()"
      class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
    >
      選擇檔案
    </button>
    <p class="mt-2 text-gray-400">或拖曳音訊檔到這裡</p>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  files: [files: FileList]
}>()

function handleDrop(e: DragEvent) {
  if (e.dataTransfer?.files) {
    emit('files', e.dataTransfer.files)
  }
}

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files) {
    emit('files', input.files)
  }
}
</script>
