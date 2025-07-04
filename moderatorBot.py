from dotenv import load_dotenv
import os
import discord
import asyncio

class Client(discord.Client):
    async def on_ready(self):
        print(f'✅ Logged in as {self.user}!')
        
        # Example: Send DM to a specific user when bot starts
        user_id = 1147144305987829801  # Replace with the target user ID
        await self.send_dm(user_id, "hello")
        
        # user_id=1147144305987829801
        # channel_id=1258351420445294643
        # await self.send_announcement(
        #     channel_id=channel_id,  
        #     message=f"What's up, guys \n@everyone"
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
TOKEN = os.getenv("moderatorBot_TOKEN")
client.run(TOKEN)

