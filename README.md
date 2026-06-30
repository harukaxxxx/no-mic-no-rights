# No mic, no rights

Discord 音效機器人，透過網頁介面管理並播放音效。

## 功能

- 網頁介面管理音效庫
- 點擊卡片即時播放音效（Discord 語音頻道）
- 管理頁面預覽播放（瀏覽器本地播放，不受 bot 連線狀態限制）
- 每個音效獨立音量調整（0-200%）
- 重複音效偵測（SHA-256 hash 比對，可選擇覆蓋）
- 搜尋、排序、釘選
- 自動跟隨指定使用者進出語音頻道
- HTTP GET 播放 API（可搭配 Stream Deck 等外部裝置觸發）

## 快速開始

### 需求

- Python 3.11+
- Node.js 18+
- uv (Python 套件管理器)
- FFmpeg

### 安裝

1. 複製 `.env.example` 為 `.env` 並填入 Discord Bot Token

**macOS / Linux:**
```bash
cp .env.example .env
```

**Windows:**
```cmd
copy .env.example .env
```

2. 編輯 `.env`，填入：
   - `DISCORD_BOT_TOKEN`: 你的 Discord bot token
   - `FOLLOW_USER_ID`: 要跟隨的 Discord user ID

3. 啟動

**macOS / Linux:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

4. 開啟瀏覽器訪問 `http://localhost:8000`

## HTTP 播放 API

可透過 HTTP GET 請求觸發播放，適合 Stream Deck 等外部裝置整合。

### 依 ID 播放

```
GET http://localhost:{PORT}/api/play/{sound_id}
```

### 依名稱播放

```
GET http://localhost:{PORT}/api/play/name/{sound_name}
```

### 回應範例

成功：
```json
{"message": "Playing", "sound": "休拉"}
```

失敗：
```json
{"error": "Bot not connected to voice channel"}
```

## 技術棧

- **後端:** Python + FastAPI + discord.py
- **前端:** Vue 3 + Vite + TailwindCSS
- **資料庫:** SQLite

## 專案結構

```
no-mic-no-rights/
├── backend/          # Python 後端
├── frontend/         # Vue 前端
├── start.sh          # macOS/Linux 啟動腳本
├── start.bat         # Windows 啟動腳本
└── pyproject.toml    # Python 專案設定
```
