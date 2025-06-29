import asyncio
import re
import ast
import math
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from script import Script
import pyrogram
from database.database import db
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils import get_search_results, get_file_details, is_subscribed, get_poster
from config import Config
import logging
from typing import List, Dict
import time

logger = logging.getLogger(__name__)

@Client.on_message(filters.group & filters.text & filters.incoming)
async def auto_filter(bot, message):
    """High-performance auto filter with optimized search"""
    
    # Performance monitoring
    start_time = time.time()
    
    # Skip if message is too short or contains unwanted patterns
    if len(message.text) < 2:
        return
    
    # Skip commands and mentions
    if message.text.startswith(('/', '@', '#')):
        return
    
    # Check if user is subscribed (if auth channel is set)
    if Config.AUTH_CHANNEL and not await is_subscribed(bot, message):
        return
    
    # Extract search query
    search_query = message.text.strip()
    
    # Remove common words and clean query
    search_query = clean_search_query(search_query)
    
    if len(search_query) < 2:
        return
    
    # Show typing indicator
    await bot.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    
    try:
        # Fast search with caching
        files = await db.get_search_results(
            query=search_query,
            max_results=Config.MAX_RESULTS
        )
        
        if not files:
            # Try spell check if enabled
            if Config.SPELL_CHECK:
                corrected_query = await spell_check(search_query)
                if corrected_query != search_query:
                    files = await db.get_search_results(
                        query=corrected_query,
                        max_results=Config.MAX_RESULTS
                    )
        
        if files:
            # Create pagination buttons
            btn = await create_pagination_buttons(files, search_query, 0)
            
            # Get movie info if IMDB is enabled
            movie_info = ""
            if Config.IMDB:
                movie_info = await get_movie_info(search_query)
            
            # Create response message
            file_count = len(files)
            response_text = f"<b>🎬 Found {file_count} results for:</b> <code>{search_query}</code>\n\n"
            
            if movie_info:
                response_text += movie_info + "\n\n"
            
            response_text += f"<b>📁 Select a file to download:</b>"
            
            # Send response
            await message.reply_text(
                text=response_text,
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.HTML
            )
            
        else:
            # No results found
            await message.reply_text(
                f"<b>❌ No results found for:</b> <code>{search_query}</code>\n\n"
                f"<b>💡 Try:</b>\n"
                f"• Different keywords\n"
                f"• Check spelling\n"
                f"• Use movie/series name only",
                parse_mode=enums.ParseMode.HTML
            )
    
    except Exception as e:
        logger.error(f"Auto filter error: {e}")
        await message.reply_text("❌ An error occurred while searching. Please try again.")
    
    # Log performance
    end_time = time.time()
    logger.info(f"Search completed in {end_time - start_time:.2f} seconds")

@Client.on_callback_query(filters.regex(r"^next_"))
async def next_page(bot, query: CallbackQuery):
    """Handle pagination - next page"""
    try:
        _, search_query, offset = query.data.split("_", 2)
        offset = int(offset)
        
        files = await db.get_search_results(
            query=search_query,
            max_results=Config.MAX_RESULTS
        )
        
        btn = await create_pagination_buttons(files, search_query, offset)
        
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
        
    except Exception as e:
        logger.error(f"Pagination error: {e}")
        await query.answer("❌ Error loading page", show_alert=True)

@Client.on_callback_query(filters.regex(r"^prev_"))
async def prev_page(bot, query: CallbackQuery):
    """Handle pagination - previous page"""
    try:
        _, search_query, offset = query.data.split("_", 2)
        offset = int(offset)
        
        files = await db.get_search_results(
            query=search_query,
            max_results=Config.MAX_RESULTS
        )
        
        btn = await create_pagination_buttons(files, search_query, offset)
        
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
        
    except Exception as e:
        logger.error(f"Pagination error: {e}")
        await query.answer("❌ Error loading page", show_alert=True)

@Client.on_callback_query(filters.regex(r"^file_"))
async def send_file(bot, query: CallbackQuery):
    """Send requested file"""
    try:
        file_id = query.data.split("_", 1)[1]
        
        file_details = await db.get_file_details(file_id)
        
        if not file_details:
            await query.answer("❌ File not found", show_alert=True)
            return
        
        # Check if user is subscribed
        if Config.AUTH_CHANNEL and not await is_subscribed(bot, query):
            await query.answer("❌ Please join our channel first", show_alert=True)
            return
        
        # Send file
        try:
            await bot.send_cached_media(
                chat_id=query.from_user.id,
                file_id=file_details['file_id'],
                caption=f"<b>📁 {file_details['file_name']}</b>\n\n"
                       f"<b>📊 Size:</b> {get_size(file_details['file_size'])}\n"
                       f"<b>🎬 Requested by:</b> {query.from_user.mention}",
                parse_mode=enums.ParseMode.HTML
            )
            
            await query.answer("✅ File sent to your PM", show_alert=False)
            
        except Exception as e:
            logger.error(f"Error sending file: {e}")
            await query.answer("❌ Error sending file", show_alert=True)
    
    except Exception as e:
        logger.error(f"File callback error: {e}")
        await query.answer("❌ An error occurred", show_alert=True)

async def create_pagination_buttons(files: List[Dict], search_query: str, offset: int) -> List[List[InlineKeyboardButton]]:
    """Create optimized pagination buttons"""
    btn = []
    
    # Calculate pagination
    total_files = len(files)
    files_per_page = Config.MAX_LIST_ELM
    total_pages = math.ceil(total_files / files_per_page)
    current_page = offset // files_per_page + 1
    
    # Get files for current page
    start_idx = offset
    end_idx = min(offset + files_per_page, total_files)
    page_files = files[start_idx:end_idx]
    
    # Create file buttons
    for file_doc in page_files:
        file_name = file_doc['file_name']
        file_size = get_size(file_doc.get('file_size', 0))
        
        # Truncate long filenames
        if len(file_name) > 60:
            file_name = file_name[:57] + "..."
        
        btn.append([
            InlineKeyboardButton(
                text=f"📁 {file_name} ({file_size})",
                callback_data=f"file_{file_doc['file_id']}"
            )
        ])
    
    # Add pagination controls
    if total_pages > 1:
        nav_buttons = []
        
        # Previous button
        if current_page > 1:
            prev_offset = max(0, offset - files_per_page)
            nav_buttons.append(
                InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{search_query}_{prev_offset}")
            )
        
        # Page info
        nav_buttons.append(
            InlineKeyboardButton(f"📄 {current_page}/{total_pages}", callback_data="pages")
        )
        
        # Next button
        if current_page < total_pages:
            next_offset = offset + files_per_page
            nav_buttons.append(
                InlineKeyboardButton("Next ➡️", callback_data=f"next_{search_query}_{next_offset}")
            )
        
        btn.append(nav_buttons)
    
    return btn

def clean_search_query(query: str) -> str:
    """Clean and optimize search query"""
    # Remove common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
    
    # Clean special characters but keep spaces and alphanumeric
    query = re.sub(r'[^\w\s]', ' ', query)
    
    # Remove extra spaces and convert to lowercase
    words = query.lower().split()
    
    # Filter out stop words and short words
    filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
    
    return ' '.join(filtered_words)

async def spell_check(query: str) -> str:
    """Simple spell check for common movie terms"""
    # This is a basic implementation - you can integrate with a proper spell checker
    corrections = {
        'moive': 'movie',
        'flim': 'film',
        'seson': 'season',
        'epsiode': 'episode',
        'documentry': 'documentary'
    }
    
    words = query.split()
    corrected_words = []
    
    for word in words:
        corrected_words.append(corrections.get(word.lower(), word))
    
    return ' '.join(corrected_words)

async def get_movie_info(query: str) -> str:
    """Get movie information from IMDB"""
    try:
        from imdb import IMDb
        
        ia = IMDb()
        movies = ia.search_movie(query)
        
        if movies:
            movie = movies[0]
            ia.update(movie)
            
            title = movie.get('title', 'N/A')
            year = movie.get('year', 'N/A')
            rating = movie.get('rating', 'N/A')
            genres = ', '.join(movie.get('genres', [])[:3])
            plot = movie.get('plot outline', 'N/A')
            
            if len(plot) > 200:
                plot = plot[:197] + "..."
            
            return (f"<b>🎬 {title} ({year})</b>\n"
                   f"<b>⭐ Rating:</b> {rating}/10\n"
                   f"<b>🎭 Genre:</b> {genres}\n"
                   f"<b>📝 Plot:</b> {plot}")
    
    except Exception as e:
        logger.error(f"IMDB error: {e}")
    
    return ""

def get_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"