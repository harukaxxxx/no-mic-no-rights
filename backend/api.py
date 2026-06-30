from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List
import os
import shutil
import hashlib
from backend.database import get_db
from backend.models import Sound, Setting

router = APIRouter()

def compute_file_hash(file_path: str) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

async def backfill_file_hashes():
    from backend.database import async_session
    async with async_session() as db:
        result = await db.execute(select(Sound).where(Sound.file_hash == None))
        sounds = result.scalars().all()
        for sound in sounds:
            file_path = f"backend/sounds/{sound.filename}"
            if os.path.exists(file_path):
                sound.file_hash = compute_file_hash(file_path)
        if sounds:
            await db.commit()

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
    name: str = Form(...),
    file: UploadFile = File(...),
    category: str = Form(""),
    tags: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    temp_path = f"backend/sounds/tmp_upload_{os.urandom(4).hex()}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_hash = compute_file_hash(temp_path)
    
    result = await db.execute(select(Sound).where(Sound.file_hash == file_hash))
    existing = result.scalar_one_or_none()
    if existing:
        os.rename(temp_path, f"backend/sounds/tmp_{file_hash}")
        return {"duplicate": True, "existing_sound": existing, "file_hash": file_hash}
    
    filename = f"{os.urandom(8).hex()}_{file.filename}"
    final_path = f"backend/sounds/{filename}"
    os.rename(temp_path, final_path)
    
    sound = Sound(
        name=name,
        filename=filename,
        category=category,
        tags=tags,
        file_hash=file_hash
    )
    db.add(sound)
    await db.commit()
    await db.refresh(sound)
    return sound

@router.post("/api/sounds/overwrite")
async def overwrite_sound(
    file_hash: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Sound).where(Sound.file_hash == file_hash))
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Original sound not found")
    
    temp_path = f"backend/sounds/tmp_{file_hash}"
    if not os.path.exists(temp_path):
        raise HTTPException(status_code=404, detail="Uploaded file not found")
    
    old_path = f"backend/sounds/{existing.filename}"
    if os.path.exists(old_path):
        os.remove(old_path)
    
    filename = f"{os.urandom(8).hex()}_{file_hash[:8]}"
    final_path = f"backend/sounds/{filename}"
    os.rename(temp_path, final_path)
    
    existing.filename = filename
    existing.file_hash = file_hash
    await db.commit()
    await db.refresh(existing)
    return existing

@router.get("/api/sounds/{sound_id}")
async def get_sound(sound_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sound).where(Sound.id == sound_id))
    sound = result.scalar_one_or_none()
    if not sound:
        raise HTTPException(status_code=404, detail="Sound not found")
    return sound

@router.get("/api/sounds/{sound_id}/preview")
async def preview_sound(sound_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sound).where(Sound.id == sound_id))
    sound = result.scalar_one_or_none()
    if not sound:
        raise HTTPException(status_code=404, detail="Sound not found")
    
    file_path = f"backend/sounds/{sound.filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(file_path, media_type="audio/mpeg")

@router.put("/api/sounds/{sound_id}")
async def update_sound(
    sound_id: int,
    name: str = None,
    category: str = None,
    tags: str = None,
    is_pinned: bool = None,
    volume: float = None,
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
    if is_pinned is not None:
        sound.is_pinned = is_pinned
    if volume is not None:
        sound.volume = volume
    
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
    
    from backend.bot import bot, player
    if not bot.voice_clients:
        raise HTTPException(status_code=400, detail="Bot not connected to voice channel")
    
    voice_client = bot.voice_clients[0]
    file_path = f"backend/sounds/{sound.filename}"
    
    try:
        await player.play(voice_client, file_path, volume=sound.volume or 1.0)
        return {"message": "Playing", "sound": sound}
    except Exception as e:
        print(f"Play error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Playback failed: {e}")

@router.get("/api/play/{sound_id}")
async def play_sound_get(sound_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sound).where(Sound.id == sound_id))
    sound = result.scalar_one_or_none()
    if not sound:
        return {"error": "Sound not found"}
    
    await db.execute(
        update(Sound).where(Sound.id == sound_id).values(play_count=Sound.play_count + 1)
    )
    await db.commit()
    
    from backend.bot import bot, player
    if not bot.voice_clients:
        return {"error": "Bot not connected to voice channel"}
    
    voice_client = bot.voice_clients[0]
    file_path = f"backend/sounds/{sound.filename}"
    
    try:
        await player.play(voice_client, file_path, volume=sound.volume or 1.0)
        return {"message": "Playing", "sound": sound.name}
    except Exception as e:
        print(f"Play error: {type(e).__name__}: {e}")
        return {"error": str(e)}

@router.get("/api/play/name/{name}")
async def play_sound_by_name(name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sound).where(Sound.name == name))
    sound = result.scalar_one_or_none()
    if not sound:
        return {"error": "Sound not found"}
    
    await db.execute(
        update(Sound).where(Sound.id == sound.id).values(play_count=Sound.play_count + 1)
    )
    await db.commit()
    
    from backend.bot import bot, player
    if not bot.voice_clients:
        return {"error": "Bot not connected to voice channel"}
    
    voice_client = bot.voice_clients[0]
    file_path = f"backend/sounds/{sound.filename}"
    
    try:
        await player.play(voice_client, file_path, volume=sound.volume or 1.0)
        return {"message": "Playing", "sound": sound.name}
    except Exception as e:
        print(f"Play error: {type(e).__name__}: {e}")
        return {"error": str(e)}

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
