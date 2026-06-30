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
