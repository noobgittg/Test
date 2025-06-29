import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, ChatAdminRequired, PeerIdInvalid
from database.database import db
from config import Config
import time

logger = logging.getLogger(__name__)

@Client.on_message(filters.command('index') & filters.user(Config.AUTH_USERS))
async def index_files(bot, message):
    """Index files from channels with high performance"""
    
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>📁 Index Files</b>\n\n"
            "<b>Usage:</b> <code>/index [channel_id/username]</code>\n"
            "<b>Example:</b> <code>/index -1001234567890</code>",
            parse_mode=enums.ParseMode.HTML
        )
    
    channel = message.command[1]
    
    try:
        # Validate channel
        chat = await bot.get_chat(channel)
        channel_id = chat.id
        channel_title = chat.title
        
    except PeerIdInvalid:
        return await message.reply_text("❌ Invalid channel ID or username")
    except Exception as e:
        return await message.reply_text(f"❌ Error accessing channel: {e}")
    
    # Start indexing
    msg = await message.reply_text(
        f"<b>🔄 Starting indexing...</b>\n\n"
        f"<b>📺 Channel:</b> {channel_title}\n"
        f"<b>🆔 ID:</b> <code>{channel_id}</code>",
        parse_mode=enums.ParseMode.HTML
    )
    
    start_time = time.time()
    total_files = 0
    duplicate_files = 0
    errors = 0
    
    try:
        # Get all messages from channel
        async for message_obj in bot.get_chat_history(channel_id):
            try:
                # Process media files
                media = None
                if message_obj.document:
                    media = message_obj.document
                elif message_obj.video:
                    media = message_obj.video
                elif message_obj.audio:
                    media = message_obj.audio
                elif message_obj.photo:
                    media = message_obj.photo
                elif message_obj.animation:
                    media = message_obj.animation
                elif message_obj.voice:
                    media = message_obj.voice
                elif message_obj.video_note:
                    media = message_obj.video_note
                elif message_obj.sticker:
                    media = message_obj.sticker
                
                if media:
                    # Add additional attributes for database
                    media.chat = message_obj.chat
                    media.message_id = message_obj.id
                    media.date = message_obj.date
                    media.file_type = get_file_type(media)
                    
                    # Save to database
                    if await db.save_file(media):
                        total_files += 1
                    else:
                        duplicate_files += 1
                    
                    # Update progress every 100 files
                    if (total_files + duplicate_files) % 100 == 0:
                        try:
                            await msg.edit_text(
                                f"<b>🔄 Indexing in progress...</b>\n\n"
                                f"<b>📺 Channel:</b> {channel_title}\n"
                                f"<b>✅ Indexed:</b> {total_files}\n"
                                f"<b>🔄 Duplicates:</b> {duplicate_files}\n"
                                f"<b>⏱️ Time:</b> {time.time() - start_time:.1f}s",
                                parse_mode=enums.ParseMode.HTML
                            )
                        except FloodWait as e:
                            await asyncio.sleep(e.value)
                        except Exception:
                            pass
            
            except Exception as e:
                errors += 1
                logger.error(f"Error processing message: {e}")
                continue
    
    except Exception as e:
        logger.error(f"Error during indexing: {e}")
        return await msg.edit_text(f"❌ Indexing failed: {e}")
    
    # Final results
    end_time = time.time()
    duration = end_time - start_time
    
    await msg.edit_text(
        f"<b>✅ Indexing completed!</b>\n\n"
        f"<b>📺 Channel:</b> {channel_title}\n"
        f"<b>✅ New files:</b> {total_files}\n"
        f"<b>🔄 Duplicates:</b> {duplicate_files}\n"
        f"<b>❌ Errors:</b> {errors}\n"
        f"<b>⏱️ Duration:</b> {duration:.1f}s\n"
        f"<b>⚡ Speed:</b> {(total_files + duplicate_files) / duration:.1f} files/sec",
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command('stats') & filters.user(Config.AUTH_USERS))
async def get_stats(bot, message):
    """Get database statistics"""
    
    msg = await message.reply_text("🔄 Getting statistics...")
    
    try:
        stats = await db.get_stats()
        
        await msg.edit_text(
            f"<b>📊 Database Statistics</b>\n\n"
            f"<b>📁 Total Files:</b> {stats['total_files']:,}\n"
            f"<b>🗄️ Active Databases:</b> {stats['active_databases']}/4\n"
            f"<b>💾 Cache Size:</b> {stats['cache_size']}\n"
            f"<b>⚡ Status:</b> Online",
            parse_mode=enums.ParseMode.HTML
        )
    
    except Exception as e:
        await msg.edit_text(f"❌ Error getting stats: {e}")

def get_file_type(media):
    """Determine file type from media object"""
    if hasattr(media, 'mime_type') and media.mime_type:
        if media.mime_type.startswith('video/'):
            return 'video'
        elif media.mime_type.startswith('audio/'):
            return 'audio'
        elif media.mime_type.startswith('image/'):
            return 'photo'
        elif media.mime_type.startswith('application/'):
            return 'document'
    
    # Fallback based on object type
    media_type = type(media).__name__.lower()
    if 'video' in media_type:
        return 'video'
    elif 'audio' in media_type:
        return 'audio'
    elif 'photo' in media_type:
        return 'photo'
    elif 'document' in media_type:
        return 'document'
    elif 'animation' in media_type:
        return 'animation'
    elif 'voice' in media_type:
        return 'voice'
    elif 'sticker' in media_type:
        return 'sticker'
    
    return 'document'