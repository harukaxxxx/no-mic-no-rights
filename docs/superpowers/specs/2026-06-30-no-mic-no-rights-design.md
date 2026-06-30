# No mic, no rights — 設計規格

## 專案概述

Discord 音效機器人，用於在語音頻道播放使用者指定的音效。透過網頁介面管理音效庫並遙控播放。

- **專案名稱：** No mic, no rights
- **位置：** `400_Project/no-mic-no-rights/`（獨立 git repo）

---

## 技術架構

```
┌─────────────────────────────────────────────────┐
│              單一 Python 進程                     │
│                                                   │
│  ┌─────────────┐    ┌──────────────────────────┐ │
│  │ discord.py   │    │ FastAPI                   │ │
│  │ Bot Client   │◄──►│ ├─ REST API (音效管理)    │ │
│  │ (Voice)      │    │ ├─ WebSocket (狀態推送)   │ │
│  │              │    │ └─ Static Files (Vue SPA) │ │
│  └─────────────┘    └──────────────────────────┘ │
│         ▲                      │                   │
│         │         ┌────────────┘                   │
│         ▼         ▼                                │
│  ┌──────────────────────┐                          │
│  │ SQLite + 本地音訊檔   │                          │
│  └──────────────────────┘                          │
└─────────────────────────────────────────────────┘
         │                      │
    Discord Voice           LAN 區域網路
    Channel                 http://<IP>:8000
```

### 技術選型

| 層 | 選擇 | 理由 |
|---|---|---|
| API | FastAPI | async、自動 OpenAPI 文件、WebSocket 支援 |
| Bot | discord.py | Python 生態最成熟、voice 支援完善 |
| DB | SQLite + SQLAlchemy | 輕量、不需要額外服務 |
| 音訊 | FFmpeg (discord.PCMVolumeTransformer) | discord.py 內建支援 |
| 前端 | Vue 3 + Vite + TailwindCSS | 輕量快速，暗色主題 |
| 前後端整合 | FastAPI serve Vue build 產物 | 單一 port、單一進程 |
| Python 環境 | uv | 管理 Python 版本和依賴 |

### 資料流

1. 使用者在網頁上傳音效 → FastAPI 存檔到 `sounds/` 資料夾 + metadata 寫入 SQLite
2. 使用者在網頁點「播放」→ FastAPI API → 透過共用 Python object 通知 discord.py bot
3. Bot 加入語音頻道 → 用 FFmpeg 播放音訊檔

---

## 網頁介面

### 頁面結構

**1. 播放頁 `/`**
- 卡片網格（responsive grid）
- 每張卡片：有封面圖 → 顯示圖片；無封面圖 → 顯示音效名稱
- 點擊卡片 → 立即播放（單音播放，中斷當前）
- 頂部：搜尋列 + 分類篩選 + 排序選項
- 排序選項：上傳日期、名稱、最常使用
- 釘選區塊：頂部獨立區塊顯示釘選音效，不受排序影響
- 快捷鍵：可指派鍵盤快捷鍵（例如：按 `1` 播放音效 A，按 `2` 播放音效 B）
- 「目前播放」指示器

**2. 管理頁 `/manage`**
- 音效列表（表格或卡片）
- 拖拽上傳區域（支援多檔）
- 編輯功能：名稱、分類、標籤、封面圖、快捷鍵
- 刪除、重新排序

**3. 設定頁 `/settings`**
- 填寫跟隨的 Discord User ID（只跟隨此 ID 進出語音頻道）
- Bot Token 設定
- Bot 狀態顯示（是否已連接語音頻道）

### 快捷鍵行為

- 監聽 `keydown` 事件，按下對應按鍵觸發播放
- 當焦點在輸入框時不觸發（避免干擾文字輸入）
- 支援單按鍵（`1`, `2`, `a`）或組合鍵（`Ctrl+1`）
- 管理介面可設定/修改快捷鍵

### 視覺風格

簡潔實用，暗色主題優先（Discord 用戶習慣），使用 Tailwind 預設風格。

---

## 資料模型

```
Sound
├── id: INTEGER PK
├── name: TEXT (顯示名稱)
├── filename: TEXT (實際檔名)
├── category: TEXT (分類)
├── tags: TEXT (逗號分隔標籤)
├── cover_image: TEXT? (封面圖檔名)
├── shortcut_key: TEXT? (快捷鍵，例如 "1", "Ctrl+A")
├── is_pinned: BOOLEAN (是否釘選)
├── play_count: INTEGER (播放次數，用於「最常使用」排序)
├── created_at: DATETIME
└── order: INTEGER (排序)

Settings
├── id: INTEGER PK
├── key: TEXT (設定名稱)
└── value: TEXT (設定值)
```

---

## Discord Bot 行為

- **Bot 名稱：** No mic, no rights
- **自動跟隨：** 偵測到指定 user ID 加入語音頻道 → bot 自動加入；user 離開 → bot 自動離開
- **播放行為：** 單音播放（新音效中斷當前）
- **Slash commands：**
  - `/status` — 查看 bot 狀態
  - `/join` — 手動加入語音頻道
  - `/leave` — 手動離開語音頻道

---

## 部署

- 區域網路直接存取
- 綁定 `0.0.0.0:8000`
- 一鍵啟動腳本 `start.sh`：
  1. `cd frontend && npm install && npm run build`
  2. `cd ../backend && uv run main.py`

---

## 專案結構

```
no-mic-no-rights/
├── backend/
│   ├── main.py              # FastAPI + discord.py 入口
│   ├── bot.py               # Discord bot 邏輯
│   ├── api.py               # REST API endpoints
│   ├── models.py            # SQLAlchemy models
│   ├── database.py          # DB 連線設定
│   └── sounds/              # 音訊檔案存放
├── frontend/
│   ├── src/
│   │   ├── views/           # 頁面元件
│   │   ├── components/      # 可重複使用元件
│   │   ├── stores/          # Pinia stores
│   │   └── App.vue
│   ├── package.json
│   └── vite.config.ts
├── pyproject.toml           # uv 專案設定
├── start.sh                 # 一鍵啟動腳本
├── .env.example
└── README.md
```
