from dotenv import load_dotenv
import os
import discord
import asyncio

class Client(discord.Client):
    async def on_ready(self):
        print(f'✅ Logged in as {self.user}!')
        
        # # Example: Send DM to a specific user when bot starts
        # user_id =   
        # await self.send_dm(user_id, "How are you?")
        
        # user_id=1146063831882285119
        # channel_id=
        # await self.send_announcement(
        #     channel_id=channel_id,  
        #     message=f"@everyone ⚽🔥 UEFA Nations League Final Tonight! 🔥⚽\n\n"
        #     "Don't miss the action! Join us at 1 AM for the epic showdown in the UEFA Nations League Final.\n"
        #     "Grab your snacks and join the stream in our voice channel!\n\n"
        #     "Who will lift the trophy? Come watch with us and chat live!"
        # )
        
    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        
    async def send_announcement(self, channel_id: int, message: str):
        await self.wait_until_ready()  
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
        
        
intents = discord.Intents.default()
intents.message_content = True

# Load environment variables from .env file
load_dotenv()
client = Client(intents=intents)
TOKEN = os.getenv("Assistant_TOKEN")
client.run(TOKEN)

