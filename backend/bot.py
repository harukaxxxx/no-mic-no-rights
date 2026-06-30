import discord
from discord.ext import commands
import asyncio
import socket
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import select, func
from backend.database import async_session
from backend.models import Sound

class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    discord_bot_token: str = ""
    follow_user_id: str = ""
    host: str = "0.0.0.0"
    port: int = 8000

bot_settings = BotSettings()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

class SoundPlayer:
    def __init__(self):
        self.current_sound = None
        self.voice_client = None
    
    async def play(self, voice_client: discord.VoiceClient, file_path: str, volume: float = 1.0):
        if voice_client.is_playing():
            voice_client.stop()
        
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(file_path), volume=volume)
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
    if not discord.opus.is_loaded():
        discord.opus.load_opus('/opt/homebrew/lib/libopus.dylib')
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
    
    print(f"[follow] {member.name}: {before.channel} -> {after.channel}")
    
    if after.channel is not None and before.channel != after.channel:
        if not bot.voice_clients:
            try:
                await after.channel.connect()
                print(f"[follow] Connected to {after.channel.name}")
            except Exception as e:
                print(f"[follow] Failed to connect: {e}")
        else:
            vc = bot.voice_clients[0]
            if vc.channel != after.channel:
                try:
                    await vc.move_to(after.channel)
                    print(f"[follow] Moved to {after.channel.name}")
                except Exception as e:
                    print(f"[follow] Failed to move: {e}")
    
    elif after.channel is None and before.channel is not None:
        if bot.voice_clients:
            for vc in bot.voice_clients:
                await vc.disconnect()
                print("[follow] Disconnected from voice channel")

def get_web_url() -> str:
    if bot_settings.host == "0.0.0.0":
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except Exception:
            ip = "localhost"
    else:
        ip = bot_settings.host
    return f"http://{ip}:{bot_settings.port}"

@bot.tree.command(name="status", description="Check bot status")
async def status(interaction: discord.Interaction):
    embed = discord.Embed(
        title="No Mic, No Rights - Status",
        color=0x5865F2
    )
    
    async with async_session() as db:
        result = await db.execute(select(func.count(Sound.id)))
        sound_count = result.scalar()
    
    if bot.voice_clients:
        vc = bot.voice_clients[0]
        voice_status = f"Connected to #{vc.channel.name}"
        if vc.is_playing():
            voice_status += "\n🎵 Currently playing"
    else:
        voice_status = "❌ Not connected"
    
    embed.add_field(name="🎤 Voice Channel", value=voice_status, inline=False)
    embed.add_field(name="🎵 Sound Library", value=f"{sound_count} sounds", inline=True)
    
    if bot_settings.follow_user_id:
        try:
            user = await bot.fetch_user(int(bot_settings.follow_user_id))
            follow_status = f"✅ @{user.name}"
        except Exception:
            follow_status = f"⚠️ User ID: {bot_settings.follow_user_id}"
    else:
        follow_status = "❌ Not configured"
    
    embed.add_field(name="👤 Following", value=follow_status, inline=True)
    embed.add_field(name="🌐 Web Interface", value=get_web_url(), inline=False)
    
    embed.set_footer(text=f"Bot: {bot.user.name}" if bot.user else "Bot not ready")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f"Connected to {channel.name}", ephemeral=True)
    else:
        await interaction.response.send_message("You're not in a voice channel", ephemeral=True)

@bot.tree.command(name="leave", description="Leave voice channel")
async def leave(interaction: discord.Interaction):
    if bot.voice_clients:
        for vc in bot.voice_clients:
            await vc.disconnect()
        await interaction.response.send_message("Disconnected", ephemeral=True)
    else:
        await interaction.response.send_message("Not connected", ephemeral=True)

async def start_bot():
    if bot_settings.discord_bot_token:
        await bot.start(bot_settings.discord_bot_token)
    else:
        print("Warning: DISCORD_BOT_TOKEN not set, bot will not start")

async def stop_bot():
    await bot.close()
