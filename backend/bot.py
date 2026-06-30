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
