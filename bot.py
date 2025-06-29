import asyncio
import logging
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.database import db
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="AutoFilterBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=Config.WORKERS,
            plugins={"root": "plugins"},
            sleep_threshold=60,
        )

    async def start(self):
        """Start the bot"""
        await super().start()
        
        # Initialize database connections
        await db.initialize()
        
        # Get bot info
        me = await self.get_me()
        
        logger.info(f"🤖 Bot started successfully!")
        logger.info(f"📝 Bot Name: {me.first_name}")
        logger.info(f"🆔 Bot Username: @{me.username}")
        logger.info(f"🔢 Bot ID: {me.id}")
        logger.info(f"🐍 Pyrogram Version: {__version__}")
        logger.info(f"📡 Layer: {layer}")
        logger.info(f"👥 Workers: {Config.WORKERS}")
        logger.info(f"🗄️ Databases: {len(db.collections)}/4 connected")
        
        # Send startup message to log channel if configured
        if Config.AUTH_USERS:
            try:
                for user_id in Config.AUTH_USERS[:1]:  # Send to first admin only
                    await self.send_message(
                        user_id,
                        f"<b>🚀 Bot Started Successfully!</b>\n\n"
                        f"<b>📝 Name:</b> {me.first_name}\n"
                        f"<b>🆔 Username:</b> @{me.username}\n"
                        f"<b>🗄️ Databases:</b> {len(db.collections)}/4 connected\n"
                        f"<b>⚡ Status:</b> Online and Ready!"
                    )
                    break
            except Exception as e:
                logger.error(f"Failed to send startup message: {e}")

    async def stop(self, *args):
        """Stop the bot"""
        logger.info("🛑 Bot stopping...")
        
        # Close database connections
        for client in db.clients:
            try:
                client.close()
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
        
        # Close Redis connection
        if db.redis_client:
            try:
                await db.redis_client.close()
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
        
        await super().stop()
        logger.info("✅ Bot stopped successfully!")

if __name__ == "__main__":
    # Create and run bot
    bot = Bot()
    bot.run()