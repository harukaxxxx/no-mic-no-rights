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
    
    from backend.bot import bot, player
    if bot.voice_clients:
        voice_client = bot.voice_clients[0]
        file_path = f"backend/sounds/{sound.filename}"
        await player.play(voice_client, file_path)
        return {"message": "Playing", "sound": sound}
    else:
        raise HTTPException(status_code=400, detail="Bot not connected to voice channel")

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
