<template>
  <div class="min-h-screen bg-gray-900 text-gray-100">
    <nav class="bg-gray-800 border-b border-gray-700">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <span class="text-xl font-bold">No mic, no rights</span>
          </div>
          <div class="flex items-center space-x-4">
            <router-link to="/" class="px-3 py-2 hover:text-white">Play</router-link>
            <router-link to="/manage" class="px-3 py-2 hover:text-white">Manage</router-link>
            <router-link to="/settings" class="px-3 py-2 hover:text-white">Settings</router-link>
          </div>
        </div>
      </div>
    </nav>
    <main class="max-w-7xl mx-auto px-4 py-8">
      <router-view />
    </main>
  </div>
</template>
