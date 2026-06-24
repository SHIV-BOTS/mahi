import random
import asyncio
from pyrogram import filters, Client
from pyrogram.types import CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup

import config
from PritiMusic import app
from PritiMusic.core.call import Lucky
from PritiMusic.misc import SUDOERS, db
from PritiMusic.utils.database import (
    get_active_chats, get_lang, is_active_chat,
    is_music_playing, is_nonadmin_chat, music_off, music_on, set_loop
)
from PritiMusic.utils.database.autoplay import is_autoplay_group, add_autoplay_group, remove_autoplay_group
from PritiMusic.utils.decorators.language import languageCB
from PritiMusic.utils.formatters import seconds_to_min
from PritiMusic.utils.inline import close_markup, stream_markup, stream_markup_timer
from PritiMusic.utils.inline.start import private_panel, support_panel
from config import BANNED_USERS, STREAM_IMG_URL, adminlist
from strings import get_string

# --- BUTTON ACTION HANDLERS ---

@app.on_callback_query(filters.regex("clone_page"))
async def clone_page_handler(client, CallbackQuery):
    await CallbackQuery.answer("Clone system active!", show_alert=True)
    await CallbackQuery.message.reply_text("🤖 **𝐂𝐋𝐎𝐍𝐄 𝐒𝐄𝐑𝐕𝐄𝐑**\n\nIs bot ko clone karne ke liye hmare support group mein contact karein.")

@app.on_callback_query(filters.regex("support_page"))
async def support_page_handler(client, CallbackQuery):
    await CallbackQuery.answer("Support Menu", show_alert=True)
    await CallbackQuery.edit_message_text(
        "**🛠 𝐒𝐔𝐏𝐏𝐎𝐑𝐓 𝐃𝐄𝐒𝐊**\n\nKripya niche diye gaye buttons ka upyog karein.",
        reply_markup=InlineKeyboardMarkup(support_panel({}))
    )

@app.on_callback_query(filters.regex("gib_source"))
async def source_page_handler(client, CallbackQuery):
    await CallbackQuery.answer("Source Code!", show_alert=True)
    await CallbackQuery.message.reply_text(f"**📂 𝐒𝐎𝐔𝐑𝐂𝐄 𝐂𝐎𝐃𝐄**\n\nBot ka source code yahan hai: {config.GITHUB}")

# --- BACK BUTTON HANDLER ---
@app.on_callback_query(filters.regex("settingsback_helper") & ~BANNED_USERS)
@languageCB
async def settings_back_helper(client, CallbackQuery, _):
    await CallbackQuery.answer()
    img = random.choice(config.START_IMG_URL) if isinstance(config.START_IMG_URL, list) else config.START_IMG_URL
    await CallbackQuery.edit_message_media(
        media=InputMediaPhoto(media=img, caption=_["start_2"].format(CallbackQuery.from_user.mention, app.mention)),
        reply_markup=InlineKeyboardMarkup(private_panel(_))
    )

# --- ADMIN COMMANDS HANDLER ---
@app.on_callback_query(filters.regex("ADMIN") & ~BANNED_USERS)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    command, chat = callback_request.split("|")
    chat_id = int(chat)
    
    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_5"], show_alert=True)
    
    mention = CallbackQuery.from_user.mention
    if not await is_nonadmin_chat(chat_id):
        if CallbackQuery.from_user.id not in SUDOERS:
            admins = adminlist.get(chat_id)
            if not admins or CallbackQuery.from_user.id not in admins:
                return await CallbackQuery.answer(_["admin_14"], show_alert=True)
                
    if command == "Pause":
        await music_off(chat_id)
        await Lucky.pause_stream(chat_id)
        await CallbackQuery.message.reply_text(_["admin_2"].format(mention), reply_markup=close_markup(_))
    elif command == "Resume":
        await music_on(chat_id)
        await Lucky.resume_stream(chat_id)
        await CallbackQuery.message.reply_text(_["admin_4"].format(mention), reply_markup=close_markup(_))
    elif command in ["Stop", "End"]:
        await Lucky.stop_stream(chat_id)
        await set_loop(chat_id, 0)
        await CallbackQuery.message.reply_text(_["admin_5"].format(mention), reply_markup=close_markup(_))
    elif command == "Autoplay":
        state = await is_autoplay_group(chat_id)
        if state:
            await remove_autoplay_group(chat_id)
            await CallbackQuery.answer("🔴 Autoplay Disabled!", show_alert=True)
        else:
            await add_autoplay_group(chat_id)
            await CallbackQuery.answer("🟢 Autoplay Enabled!", show_alert=True)
    await CallbackQuery.answer()

# --- TIMER MARKUP UPDATER ---
async def markup_timer():
    while True:
        await asyncio.sleep(7)
        try:
            active_chats = await get_active_chats()
            for chat_id in active_chats:
                if not await is_music_playing(chat_id): continue
                playing = db.get(chat_id)
                if not playing or int(playing[0].get("seconds", 0)) == 0: continue
                mystic = playing[0].get("mystic")
                if not mystic: continue
                try:
                    lang = await get_lang(chat_id)
                    _ = get_string(lang)
                except: _ = get_string("en")
                buttons = stream_markup_timer(_, chat_id, seconds_to_min(playing[0]["played"]), playing[0]["dur"])
                await mystic.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
        except: pass

asyncio.create_task(markup_timer())
        
