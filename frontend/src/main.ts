import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

import PlayView from './views/PlayView.vue'
import ManageView from './views/ManageView.vue'
import SettingsView from './views/SettingsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: PlayView },
    { path: '/manage', component: ManageView },
    { path: '/settings', component: SettingsView },
  ],
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
