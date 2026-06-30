# No mic, no rights Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Discord soundboard bot with web interface for managing and playing sound effects in voice channels.

**Architecture:** Single Python process running FastAPI (serving REST API + Vue SPA static files) and discord.py bot. SQLite for metadata, local filesystem for audio files. Vue 3 + Vite + TailwindCSS frontend.

**Tech Stack:** Python (uv), FastAPI, discord.py, SQLite + SQLAlchemy, Vue 3, Vite, TailwindCSS

---

## File Structure

```
no-mic-no-rights/
├── backend/
│   ├── main.py              # FastAPI app + discord.py bot startup
│   ├── bot.py               # Discord bot logic (voice, playback)
│   ├── api.py               # REST API endpoints (sounds, settings)
│   ├── models.py            # SQLAlchemy models (Sound, Settings)
│   ├── database.py          # Database connection, session management
│   └── sounds/              # Audio file storage (gitignored)
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── PlayView.vue      # Card grid, play sounds
│   │   │   ├── ManageView.vue    # Upload, edit, delete
│   │   │   └── SettingsView.vue  # Bot config
│   │   ├── components/
│   │   │   ├── SoundCard.vue     # Individual sound card
│   │   │   ├── UploadArea.vue    # Drag-drop upload
│   │   │   └── NowPlaying.vue    # Current playback indicator
│   │   ├── stores/
│   │   │   └── sounds.ts         # Pinia store for sounds
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── postcss.config.js
├── pyproject.toml           # uv project config
├── start.sh                 # One-command startup
├── .env.example
└── .gitignore
```

---

## Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `backend/sounds/.gitkeep`

- [ ] **Step 1: Initialize uv project**

Run: `cd /Users/haruka/haruka-alt-ego/400_Project/no-mic-no-rights && uv init --no-readme`

Expected: Creates `pyproject.toml` and `.python-version`

- [ ] **Step 2: Update pyproject.toml**

```toml
[project]
name = "no-mic-no-rights"
version = "0.1.0"
description = "Discord soundboard bot with web interface"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy>=2.0.0",
    "aiosqlite>=0.20.0",
    "discord.py>=2.4.0",
    "python-dotenv>=1.0.0",
    "python-multipart>=0.0.12",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
]

[project.scripts]
start = "backend.main:main"
```

- [ ] **Step 3: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
*.egg-info/

# Node
node_modules/
dist/
.DS_Store

# Project specific
backend/sounds/*
!backend/sounds/.gitkeep
.env
*.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Superpowers
.superpowers/
```

- [ ] **Step 4: Create .env.example**

```env
DISCORD_BOT_TOKEN=your_bot_token_here
FOLLOW_USER_ID=your_discord_user_id
DATABASE_URL=sqlite+aiosqlite:///./soundboard.db
HOST=0.0.0.0
PORT=8000
```

- [ ] **Step 5: Create sounds directory**

```bash
mkdir -p backend/sounds
touch backend/sounds/.gitkeep
```

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "chore: initial project scaffolding"
```

---

## Task 2: Database Models

**Files:**
- Create: `backend/database.py`
- Create: `backend/models.py`
- Create: `backend/__init__.py`

- [ ] **Step 1: Create backend package**

```bash
touch backend/__init__.py
```

- [ ] **Step 2: Create database.py**

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./soundboard.db"
    
    class Config:
        env_file = ".env"

settings = Settings()

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with async_session() as session:
        yield session
```

- [ ] **Step 3: Create models.py**

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from backend.database import Base

class Sound(Base):
    __tablename__ = "sounds"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    category = Column(String, default="")
    tags = Column(String, default="")
    cover_image = Column(String, nullable=True)
    shortcut_key = Column(String, nullable=True)
    is_pinned = Column(Boolean, default=False)
    play_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    order = Column(Integer, default=0)

class Setting(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=True)
```

- [ ] **Step 4: Test database initialization**

```bash
uv run python -c "
import asyncio
from backend.database import init_db
from backend.models import Sound, Setting

async def test():
    await init_db()
    print('Database initialized successfully')

asyncio.run(test())
"
```

Expected: `Database initialized successfully`

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: add database models and initialization"
```

---

## Task 3: FastAPI Application

**Files:**
- Create: `backend/api.py`
- Create: `backend/main.py`

- [ ] **Step 1: Create api.py with basic endpoints**

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
import os
import shutil
from backend.database import get_db
from backend.models import Sound, Setting

router = APIRouter()

@router.get("/api/sounds")
async def list_sounds(
    category: str = None,
    search: str = None,
    sort: str = "created_at",
    db: AsyncSession = Depends(get_db)
):
    query = select(Sound)
    
    if category:
        query = query.where(Sound.category == category)
    if search:
        query = query.where(Sound.name.contains(search))
    
    if sort == "name":
        query = query.order_by(Sound.name)
    elif sort == "play_count":
        query = query.order_by(Sound.play_count.desc())
    else:
        query = query.order_by(Sound.created_at.desc())
    
    result = await db.execute(query)
    sounds = result.scalars().all()
    return sounds

@router.post("/api/sounds")
async def create_sound(
    name: str,
    file: UploadFile = File(...),
    category: str = "",
    tags: str = "",
    db: AsyncSession = Depends(get_db)
):
    filename = f"{os.urandom(8).hex()}_{file.filename}"
    file_path = f"backend/sounds/{filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    sound = Sound(
        name=name,
        filename=filename,
        category=category,
        tags=tags
    )
    db.add(sound)
    await db.commit()
    await db.refresh(sound)
    return sound

@router.get("/api/sounds/{sound_id}")
async def get_sound(sound_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sound).where(Sound.id == sound_id))
    sound = result.scalar_one_or_none()
    if not sound:
        raise HTTPException(status_code=404, detail="Sound not found")
    return sound

@router.put("/api/sounds/{sound_id}")
async def update_sound(
    sound_id: int,
    name: str = None,
    category: str = None,
    tags: str = None,
    shortcut_key: str = None,
    is_pinned: bool = None,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Sound).where(Sound.id == sound_id))
    sound = result.scalar_one_or_none()
    if not sound:
        raise HTTPException(status_code=404, detail="Sound not found")
    
    if name is not None:
        sound.name = name
    if category is not None:
        sound.category = category
    if tags is not None:
        sound.tags = tags
    if shortcut_key is not None:
        sound.shortcut_key = shortcut_key
    if is_pinned is not None:
        sound.is_pinned = is_pinned
    
    await db.commit()
    await db.refresh(sound)
    return sound

@router.delete("/api/sounds/{sound_id}")
async def delete_sound(sound_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sound).where(Sound.id == sound_id))
    sound = result.scalar_one_or_none()
    if not sound:
        raise HTTPException(status_code=404, detail="Sound not found")
    
    file_path = f"backend/sounds/{sound.filename}"
    if os.path.exists(file_path):
        os.remove(file_path)
    
    await db.delete(sound)
    await db.commit()
    return {"message": "Sound deleted"}

@router.post("/api/sounds/{sound_id}/play")
async def play_sound(sound_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sound).where(Sound.id == sound_id))
    sound = result.scalar_one_or_none()
    if not sound:
        raise HTTPException(status_code=404, detail="Sound not found")
    
    await db.execute(
        update(Sound).where(Sound.id == sound_id).values(play_count=Sound.play_count + 1)
    )
    await db.commit()
    
    return {"message": "Playing", "sound": sound}

@router.get("/api/settings")
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Setting))
    settings = result.scalars().all()
    return {s.key: s.value for s in settings}

@router.put("/api/settings/{key}")
async def update_setting(key: str, value: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        db.add(setting)
    
    await db.commit()
    return {"key": key, "value": value}
```

- [ ] **Step 2: Create main.py**

```python
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn
from backend.database import init_db
from backend.api import router as api_router
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"

app_settings = AppSettings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")

def main():
    uvicorn.run(
        "backend.main:app",
        host=app_settings.host,
        port=app_settings.port,
        reload=True
    )

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Test API startup**

```bash
uv run python -c "from backend.main import app; print('FastAPI app created')"
```

Expected: `FastAPI app created`

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: add FastAPI application with sound CRUD endpoints"
```

---

## Task 4: Discord Bot

**Files:**
- Create: `backend/bot.py`

- [ ] **Step 1: Create bot.py**

```python
import discord
from discord.ext import commands
import asyncio
from pydantic_settings import BaseSettings

class BotSettings(BaseSettings):
    discord_bot_token: str = ""
    follow_user_id: str = ""
    
    class Config:
        env_file = ".env"

bot_settings = BotSettings()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

class SoundPlayer:
    def __init__(self):
        self.current_sound = None
        self.voice_client = None
    
    async def play(self, voice_client: discord.VoiceClient, file_path: str):
        if voice_client.is_playing():
            voice_client.stop()
        
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(file_path))
        self.current_sound = file_path
        self.voice_client = voice_client
        voice_client.play(source)
    
    async def stop(self):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
        self.current_sound = None

player = SoundPlayer()

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    if not bot_settings.follow_user_id:
        return
    
    if str(member.id) != bot_settings.follow_user_id:
        return
    
    if before.channel is None and after.channel is not None:
        if member.voice and member.voice.channel:
            channel = member.voice.channel
            if not bot.voice_clients:
                await channel.connect()
                print(f"Connected to {channel.name}")
    
    elif before.channel is not None and after.channel is None:
        if bot.voice_clients:
            for vc in bot.voice_clients:
                await vc.disconnect()
                print("Disconnected from voice channel")

@bot.tree.command(name="status", description="Check bot status")
async def status(interaction: discord.Interaction):
    if bot.voice_clients:
        vc = bot.voice_clients[0]
        status_msg = f"Connected to {vc.channel.name}"
        if vc.is_playing():
            status_msg += " (currently playing)"
    else:
        status_msg = "Not connected to any voice channel"
    
    await interaction.response.send_message(status_msg)

@bot.tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f"Connected to {channel.name}")
    else:
        await interaction.response.send_message("You're not in a voice channel")

@bot.tree.command(name="leave", description="Leave voice channel")
async def leave(interaction: discord.Interaction):
    if bot.voice_clients:
        for vc in bot.voice_clients:
            await vc.disconnect()
        await interaction.response.send_message("Disconnected")
    else:
        await interaction.response.send_message("Not connected")

async def start_bot():
    if bot_settings.discord_bot_token:
        await bot.start(bot_settings.discord_bot_token)
    else:
        print("Warning: DISCORD_BOT_TOKEN not set, bot will not start")

async def stop_bot():
    await bot.close()
```

- [ ] **Step 2: Test bot import**

```bash
uv run python -c "from backend.bot import bot, player; print('Bot module loaded')"
```

Expected: `Bot module loaded`

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "feat: add Discord bot with voice channel following"
```

---

## Task 5: Integration

**Files:**
- Modify: `backend/main.py`
- Modify: `backend/api.py`

- [ ] **Step 1: Update main.py to start bot**

```python
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn
from backend.database import init_db
from backend.api import router as api_router
from backend.bot import start_bot, stop_bot, player
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"

app_settings = AppSettings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    bot_task = asyncio.create_task(start_bot())
    yield
    await stop_bot()
    bot_task.cancel()

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")

def main():
    uvicorn.run(
        "backend.main:app",
        host=app_settings.host,
        port=app_settings.port,
        reload=True
    )

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Update api.py play endpoint**

```python
@router.post("/api/sounds/{sound_id}/play")
async def play_sound(sound_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sound).where(Sound.id == sound_id))
    sound = result.scalar_one_or_none()
    if not sound:
        raise HTTPException(status_code=404, detail="Sound not found")
    
    await db.execute(
        update(Sound).where(Sound.id == sound_id).values(play_count=Sound.play_count + 1)
    )
    await db.commit()
    
    from backend.bot import bot, player
    if bot.voice_clients:
        voice_client = bot.voice_clients[0]
        file_path = f"backend/sounds/{sound.filename}"
        await player.play(voice_client, file_path)
        return {"message": "Playing", "sound": sound}
    else:
        raise HTTPException(status_code=400, detail="Bot not connected to voice channel")
```

- [ ] **Step 3: Test integration**

```bash
uv run python -c "
from backend.main import app
from backend.bot import bot, player
print('Integration successful')
"
```

Expected: `Integration successful`

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: integrate FastAPI and Discord bot"
```

---

## Task 6: Vue Project Setup

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`

- [ ] **Step 1: Create Vue project structure**

```bash
mkdir -p frontend/src/{views,components,stores}
```

- [ ] **Step 2: Create package.json**

```json
{
  "name": "no-mic-no-rights-frontend",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.4.0",
    "pinia": "^2.2.0",
    "axios": "^1.7.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.0",
    "vite": "^5.4.0",
    "vue-tsc": "^2.1.0",
    "typescript": "^5.5.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

- [ ] **Step 3: Create vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

- [ ] **Step 4: Create tailwind.config.js**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {},
  },
  plugins: [],
}
```

- [ ] **Step 5: Create postcss.config.js**

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

- [ ] **Step 6: Create index.html**

```html
<!DOCTYPE html>
<html lang="zh-TW" class="dark">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>No mic, no rights</title>
  </head>
  <body class="dark bg-gray-900 text-gray-100">
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 7: Create src/main.ts**

```typescript
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
```

- [ ] **Step 8: Create src/style.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 9: Create src/App.vue**

```vue
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
```

- [ ] **Step 10: Install dependencies**

```bash
cd frontend && npm install
```

- [ ] **Step 11: Commit**

```bash
cd .. && git add .
git commit -m "feat: setup Vue 3 + Vite + TailwindCSS frontend"
```

---

## Task 7: Pinia Store

**Files:**
- Create: `frontend/src/stores/sounds.ts`

- [ ] **Step 1: Create sounds store**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export interface Sound {
  id: number
  name: string
  filename: string
  category: string
  tags: string
  cover_image: string | null
  shortcut_key: string | null
  is_pinned: boolean
  play_count: number
  created_at: string
}

export const useSoundsStore = defineStore('sounds', () => {
  const sounds = ref<Sound[]>([])
  const loading = ref(false)
  const currentPlaying = ref<Sound | null>(null)

  async function fetchSounds() {
    loading.value = true
    try {
      const response = await axios.get('/api/sounds')
      sounds.value = response.data
    } catch (error) {
      console.error('Failed to fetch sounds:', error)
    } finally {
      loading.value = false
    }
  }

  async function playSound(sound: Sound) {
    try {
      await axios.post(`/api/sounds/${sound.id}/play`)
      currentPlaying.value = sound
      sound.play_count++
    } catch (error) {
      console.error('Failed to play sound:', error)
      alert('播放失敗：' + (error.response?.data?.detail || '未知錯誤'))
    }
  }

  async function uploadSound(file: File, name: string, category: string = '', tags: string = '') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('name', name)
    formData.append('category', category)
    formData.append('tags', tags)
    
    try {
      const response = await axios.post('/api/sounds', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      sounds.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('Failed to upload sound:', error)
      throw error
    }
  }

  async function updateSound(id: number, data: Partial<Sound>) {
    try {
      const response = await axios.put(`/api/sounds/${id}`, null, { params: data })
      const index = sounds.value.findIndex(s => s.id === id)
      if (index !== -1) {
        sounds.value[index] = { ...sounds.value[index], ...data }
      }
      return response.data
    } catch (error) {
      console.error('Failed to update sound:', error)
      throw error
    }
  }

  async function deleteSound(id: number) {
    try {
      await axios.delete(`/api/sounds/${id}`)
      sounds.value = sounds.value.filter(s => s.id !== id)
    } catch (error) {
      console.error('Failed to delete sound:', error)
      throw error
    }
  }

  return {
    sounds,
    loading,
    currentPlaying,
    fetchSounds,
    playSound,
    uploadSound,
    updateSound,
    deleteSound,
  }
})
```

- [ ] **Step 2: Commit**

```bash
git add .
git commit -m "feat: add Pinia store for sounds management"
```

---

## Task 8: Play View

**Files:**
- Create: `frontend/src/views/PlayView.vue`
- Create: `frontend/src/components/SoundCard.vue`
- Create: `frontend/src/components/NowPlaying.vue`

- [ ] **Step 1: Create SoundCard.vue**

```vue
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
```

- [ ] **Step 2: Create NowPlaying.vue**

```vue
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
```

- [ ] **Step 3: Create PlayView.vue**

```vue
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
```

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: add play view with card grid and shortcuts"
```

---

## Task 9: Manage View

**Files:**
- Create: `frontend/src/views/ManageView.vue`
- Create: `frontend/src/components/UploadArea.vue`

- [ ] **Step 1: Create UploadArea.vue**

```vue
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
      @click="$refs.fileInput.click()"
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
```

- [ ] **Step 2: Create ManageView.vue**

```vue
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
```

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "feat: add manage view with upload and edit"
```

---

## Task 10: Settings View

**Files:**
- Create: `frontend/src/views/SettingsView.vue`

- [ ] **Step 1: Create SettingsView.vue**

```vue
<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">設定</h1>
    
    <div class="space-y-6 max-w-2xl">
      <div>
        <label class="block text-sm font-medium mb-2">跟隨的 Discord User ID</label>
        <input 
          v-model="followUserId"
          @blur="saveSetting('follow_user_id', followUserId)"
          type="text"
          placeholder="例如：123456789012345678"
          class="w-full bg-gray-800 border border-gray-700 rounded px-4 py-2"
        />
        <p class="mt-1 text-sm text-gray-400">Bot 會自動跟隨此使用者進出語音頻道</p>
      </div>

      <div>
        <label class="block text-sm font-medium mb-2">Bot Token</label>
        <input 
          v-model="botToken"
          @blur="saveSetting('discord_bot_token', botToken)"
          type="password"
          placeholder="your_bot_token"
          class="w-full bg-gray-800 border border-gray-700 rounded px-4 py-2"
        />
      </div>

      <div class="bg-gray-800 rounded-lg p-4">
        <h2 class="font-medium mb-2">Bot 狀態</h2>
        <p class="text-gray-400">Bot 目前{{ botConnected ? '已' : '未' }}連線</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const followUserId = ref('')
const botToken = ref('')
const botConnected = ref(false)

async function loadSettings() {
  try {
    const response = await axios.get('/api/settings')
    const settings = response.data
    followUserId.value = settings.follow_user_id || ''
    botToken.value = settings.discord_bot_token || ''
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}

async function saveSetting(key: string, value: string) {
  try {
    await axios.put(`/api/settings/${key}`, null, { params: { value } })
  } catch (error) {
    console.error('Failed to save setting:', error)
  }
}

onMounted(() => {
  loadSettings()
})
</script>
```

- [ ] **Step 2: Commit**

```bash
git add .
git commit -m "feat: add settings view"
```

---

## Task 11: Start Script

**Files:**
- Create: `start.sh`

- [ ] **Step 1: Create start.sh**

```bash
#!/bin/bash

set -e

echo "=== No mic, no rights ==="
echo ""

if [ ! -f .env ]; then
  echo "Warning: .env file not found. Copying from .env.example..."
  cp .env.example .env
  echo "Please edit .env and add your Discord bot token."
  echo ""
fi

echo "Installing Python dependencies..."
uv sync

echo "Installing frontend dependencies..."
cd frontend
npm install

echo "Building frontend..."
npm run build
cd ..

echo ""
echo "Starting server..."
echo "Access the web interface at: http://$(hostname -I | awk '{print $1}'):8000"
echo "Or: http://localhost:8000"
echo ""

uv run python -m backend.main
```

- [ ] **Step 2: Make executable**

```bash
chmod +x start.sh
```

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "feat: add one-command start script"
```

---

## Task 12: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README.md**

```markdown
# No mic, no rights

Discord 音效機器人，透過網頁介面管理並播放音效。

## 功能

- 網頁介面管理音效庫
- 點擊卡片即時播放音效
- 自動跟隨指定使用者進出語音頻道
- 支援快捷鍵、釘選、分類、搜尋
- 單音播放模式

## 快速開始

### 需求

- Python 3.11+
- Node.js 18+
- uv (Python 套件管理器)
- FFmpeg

### 安裝

1. 複製 `.env.example` 為 `.env` 並填入 Discord Bot Token

```bash
cp .env.example .env
```

2. 編輯 `.env`，填入：
   - `DISCORD_BOT_TOKEN`: 你的 Discord bot token
   - `FOLLOW_USER_ID`: 要跟隨的 Discord user ID

3. 啟動

```bash
./start.sh
```

4. 開啟瀏覽器訪問 `http://localhost:8000`

## 技術棧

- **後端:** Python + FastAPI + discord.py
- **前端:** Vue 3 + Vite + TailwindCSS
- **資料庫:** SQLite

## 專案結構

```
no-mic-no-rights/
├── backend/          # Python 後端
├── frontend/         # Vue 前端
├── start.sh          # 一鍵啟動腳本
└── pyproject.toml    # Python 專案設定
```
```

- [ ] **Step 2: Commit**

```bash
git add .
git commit -m "docs: add README"
```

---

## Task 13: Final Integration Test

- [ ] **Step 1: Build frontend**

```bash
cd frontend && npm run build
```

Expected: Build completes successfully, creates `dist/` directory

- [ ] **Step 2: Test startup**

```bash
cd .. && uv run python -m backend.main
```

Expected: Server starts on `http://0.0.0.0:8000`

- [ ] **Step 3: Test web interface**

Open browser to `http://localhost:8000`

Expected: See play page with empty state

- [ ] **Step 4: Test upload**

1. Go to `/manage`
2. Upload an audio file
3. Verify it appears in the list

- [ ] **Step 5: Test play**

1. Go to `/`
2. Click on uploaded sound card
3. Verify sound plays (if bot is connected to voice channel)

- [ ] **Step 6: Final commit**

```bash
git add .
git commit -m "chore: final integration test"
```

---

## Summary

This plan implements a Discord soundboard bot with:

- **Backend:** FastAPI + discord.py in single process
- **Frontend:** Vue 3 + Vite + TailwindCSS
- **Features:** Upload, manage, play sounds with shortcuts and pinning
- **Deployment:** One-command startup with `start.sh`

Total estimated time: 2-3 hours for implementation.
