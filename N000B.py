from dotenv import load_dotenv
import os
import discord 
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio
import asyncio
import re
from yt_dlp import YoutubeDL

ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'extract_flat': 'in_playlist'
}
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
ytdl = YoutubeDL(ytdl_format_options)


class Client(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Register a tree on the Bot for slash commands


    async def setup_hook(self):
        await self.tree.sync()
        print(f"Slash commands synced globally.")
        
    async def on_ready(self):
        print(f'✅ Logged in as {self.user} (ID: {self.user.id})!')
        
        # Send DM to a specific user when bot starts
        # user_id = 1147144305987829801  # Replace with the target user ID
        # await self.send_dm(user_id, "Hello there! I'm your personal assistant. How can I help you today?")

        # try:
        #     guild = discord.Object(id=1253592675945545770)
        #     synced = await self.tree.sync(guild=guild)
        #     print(f'Synced {len(synced)} commands to the guild: {guild.id}')
        # except Exception as e:
        #     print(f'Error syncing commands: {e}')


        # Send an announcement or reacting to a specific channel and message
        # await self.react_to_message(channel_id=1258351420445294643, message_id=1377302829685014548, emoji="🤓")
        # user_id = 1147144305987829801
        # channel_id = 1260115216507601019
        # await self.send_announcement(
        #     channel_id=channel_id,  
        #     message=f"Kire CG 4 naki? Stat pora sesh shob? <@{user_id}>"
        # )


    # Send an announcement to a specific channel
    async def send_announcement(self, channel_id: int, message: str):
        await self.wait_until_ready()  # Ensure bot is ready before sending
        channel = self.get_channel(channel_id)
        if channel:
            await channel.send(message)
        else:
            print(f"❌ Channel with ID {channel_id} not found.")

    # New method to send a DM to a user
    async def send_dm(self, user_id: int, message: str):
        await self.wait_until_ready()
        try:
            user = await self.fetch_user(user_id)
            await user.send(message)
            print(f"✅ DM sent to user {user_id}")
            return True
        except discord.errors.NotFound:
            print(f"❌ User with ID {user_id} not found.")
            return False
        except discord.errors.Forbidden:
            print(f"❌ Cannot send DM to user with ID {user_id}. They might have DMs disabled.")
            return False
    
    # React to a specific message in a channel
    async def react_to_message(self, channel_id: int, message_id: int, emoji: str):
        channel = await client.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)
        await message.add_reaction(emoji)

    # Handle incoming messages
    async def on_message(self, message):
        if message.author == self.user:
            return
        print(f'Message from {message.author}: {message.content}')
        if message.content.startswith('hello'):
            await message.channel.send(f'Hello there, {message.author.mention}!')
        if message.content.startswith('hi'):
            await message.channel.send(f'Hi {message.author.mention}! How can I help you?')
        if message.content.startswith('wassup'):
            await message.channel.send(f'Eito bro! Choltese konorokom :3')
            await message.channel.send(f'Tomar ki khobor?')
        if message.content.startswith('bye'):
            await message.channel.send(f'Goodbye {message.author.mention}! Have a great day!')


    # Use raw events for consistent reaction handling in channels and DMs
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        user = self.get_user(payload.user_id) or await self.fetch_user(payload.user_id)
        channel = await self.fetch_channel(payload.channel_id)
        emoji = payload.emoji.name if hasattr(payload.emoji, 'name') else str(payload.emoji)
        await channel.send(f'{user.name} reacted with {emoji}!')

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        user = self.get_user(payload.user_id) or await self.fetch_user(payload.user_id)
        channel = await self.fetch_channel(payload.channel_id)
        emoji = payload.emoji.name if hasattr(payload.emoji, 'name') else str(payload.emoji)
        await channel.send(f'{user.name} removed their reaction {emoji}!')
    # async def on_reaction_add(self, reaction, user):
    #     await reaction.message.channel.send(f'{user.name} reacted with {reaction.emoji}!')
    # async def on_reaction_remove(self, reaction, user):
    #     await reaction.message.channel.send(f'{user.name} removed their reaction {reaction.emoji}!')


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.voice_states = True
client = Client(command_prefix="!", intents=intents)
#GUILD ID
GUILD_ID = discord.Object(id=1253592675945545770)

# Music Slash Commands (Global Slash Commands)
# ------------------------------------------------------------------------------------------------------------------
@client.tree.command(name="join", description="Bot joins your current voice channel.")
async def join(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        return await interaction.response.send_message("❌ You are not in a voice channel.", ephemeral=True)
    channel = interaction.user.voice.channel
    await channel.connect()
    await interaction.response.send_message(f"✅ Joined **{channel.name}**.")

@client.tree.command(name="leave", description="Bot leaves its current voice channel.")
async def leave(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_connected():
        await vc.disconnect()
        await interaction.response.send_message("👋 Left the voice channel.")
    else:
        await interaction.response.send_message("❌ I'm not connected to any voice channel.", ephemeral=True)

@client.tree.command(name="play", description="Plays audio from a YouTube URL.")
@app_commands.describe(url="The YouTube video URL to stream audio from.")
async def play(interaction: discord.Interaction, url: str):
    # Ensure the bot is connected
    vc = interaction.guild.voice_client
    if not vc or not vc.is_connected():
        if interaction.user.voice and interaction.user.voice.channel:
            vc = await interaction.user.voice.channel.connect()
        else:
            return await interaction.response.send_message("❌ You must be in a voice channel or I must already be connected.", ephemeral=True)

    # Extract audio stream info
    await interaction.response.defer()  # Acknowledge before processing
    try:
        info = await client.loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
    except Exception as e:
        return await interaction.followup.send(f"❌ Could not retrieve audio info:\n```{e}```")
    
    audio_url = info['url']
    title = info.get('title', 'Unknown Title')

    # Play via FFmpeg
    vc.play(FFmpegPCMAudio(audio_url, **ffmpeg_options))
    await interaction.followup.send(f"▶️ Now playing: **{title}**")

@client.tree.command(name="pause", description="Pauses current audio playback.")
async def pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("⏸️ Paused playback.")
    else:
        await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)

@client.tree.command(name="resume", description="Resumes paused audio playback.")
async def resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message("▶️ Resumed playback.")
    else:
        await interaction.response.send_message("❌ Playback is not paused.", ephemeral=True)

@client.tree.command(name="stop", description="Stops audio playback and clears the queue.")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and (vc.is_playing() or vc.is_paused()):
        vc.stop()
        await interaction.response.send_message("⏹️ Stopped playback.")
    else:
        await interaction.response.send_message("❌ Nothing to stop.", ephemeral=True)
# ------------------------------------------------------------------------------------------------------------------


# not Global Slash Commands
# says hello
@client.tree.command(name="hello", description="Says hello!", guild=GUILD_ID)
async def sayHello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hello {interaction.user.mention}!')

# prints whatever you give it
@client.tree.command(name="printer", description="I will print whatever you give me!", guild=GUILD_ID)
async def Printer(interaction: discord.Interaction, printer: str):
    await interaction.response.send_message(printer)

# Reminder Command: /remind <duration> <note>
@client.tree.command(
    name="remind",
    description="Set a reminder. Time format: combination of <number><unit> segments (e.g., 1h 15m 30s, 2d, 45s)",
    guild=GUILD_ID
)
async def remind(
    interaction: discord.Interaction,
    duration: str,
    *,
    note: str
):
    # Parse multiple time segments (e.g., '1h 15m 30s')
    pattern = r"(\d+)([smhd])"
    matches = re.findall(pattern, duration.replace(' ', ''))
    if not matches:
        return await interaction.response.send_message(
            "❌ Invalid time format. Use e.g. `1h 15m`, `2d`, `30m`, `45s`, combining segments as needed."
        )

    total_seconds = 0
    for amount_str, unit in matches:
        amount = int(amount_str)
        if unit == 's':
            total_seconds += amount
        elif unit == 'm':
            total_seconds += amount * 60
        elif unit == 'h':
            total_seconds += amount * 3600
        elif unit == 'd':
            total_seconds += amount * 86400

    # Acknowledge reminder setup
    await interaction.response.send_message(
        f'⏰ Got it! I will remind you in `{duration}`.'
    )

    # Wait and send reminder
    await asyncio.sleep(total_seconds)
    channel = await interaction.channel.fetch()
    await channel.send(
        f'🔔 {interaction.user.mention}, here is your reminder: {note}'
    )

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("N000B_TOKEN")
# Run the bot
if __name__ == '__main__':
    client.run(TOKEN)