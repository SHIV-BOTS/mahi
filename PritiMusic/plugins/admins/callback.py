import random
import asyncio
from pyrogram import filters
from pyrogram.types import InputMediaPhoto, InlineKeyboardMarkup
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
from PritiMusic.utils.thumbnails import get_thumb
from PritiMusic.utils.inline.start import private_panel, support_panel
from config import BANNED_USERS, STREAM_IMG_URL, adminlist
from strings import get_string

# --- SYNCED BUTTON CALLBACK HANDLERS ---

@app.on_callback_query(filters.regex("clone_page"))
async def clone_page_handler(client, CallbackQuery):
    await CallbackQuery.answer("Clone system!", show_alert=True)
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

# --- ADMIN COMMANDS ---
@app.on_callback_query(filters.regex("ADMIN") & ~BANNED_USERS)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    command, chat = callback_request.split("|")
    
    # Extract chat_id properly in case it has additional data
    if "_" in str(chat):
        bet = chat.split("_")
        chat = bet[0]
    chat_id = int(chat)
    
    if not await is_active_chat(chat_id): return await CallbackQuery.answer(_["general_5"], show_alert=True)
    
    mention = CallbackQuery.from_user.mention
    if not await is_nonadmin_chat(chat_id):
        if CallbackQuery.from_user.id not in SUDOERS:
            admins = adminlist.get(chat_id)
            if not admins or CallbackQuery.from_user.id not in admins:
                return await CallbackQuery.answer(_["admin_14"], show_alert=True)
    
    if command == "Pause":
        await music_off(chat_id); await Lucky.pause_stream(chat_id)
        await CallbackQuery.message.reply_text(_["admin_2"].format(mention), reply_markup=close_markup(_))
    elif command == "Resume":
        await music_on(chat_id); await Lucky.resume_stream(chat_id)
        await CallbackQuery.message.reply_text(_["admin_4"].format(mention), reply_markup=close_markup(_))
    elif command in ["Stop", "End"]:
        await Lucky.stop_stream(chat_id); await set_loop(chat_id, 0)
        await CallbackQuery.message.reply_text(_["admin_5"].format(mention), reply_markup=close_markup(_))
    elif command == "Autoplay":
        state = await is_autoplay_group(chat_id)
        if state: 
            await remove_autoplay_group(chat_id)
            await CallbackQuery.answer("🔴 Autoplay Disabled!", show_alert=True)
        else: 
            await add_autoplay_group(chat_id)
            await CallbackQuery.answer("🟢 Autoplay Enabled!", show_alert=True)
    
    # 🔴 MISSING SKIP AND REPLAY LOGIC ADDED BACK HERE 🔴
    elif command in ["Skip", "Replay"]:
        check = db.get(chat_id)
        if not check:
            return await CallbackQuery.answer("Queue khali hai!", show_alert=True)
            
        if command == "Skip":
            await CallbackQuery.answer("Skipping...", show_alert=True)
            clients = await Lucky.get_active_clients(chat_id)
            pytgcalls_client = clients[0] if clients else Lucky.one
            await Lucky.change_stream(pytgcalls_client, chat_id)
            await CallbackQuery.edit_message_text(f"➻ sᴛʀᴇᴀᴍ sᴋɪᴩᴩᴇᴅ 🎄\n└ʙʏ : {mention}", reply_markup=close_markup(_))
        else: # Replay Logic
            await CallbackQuery.answer("Replaying...", show_alert=True)
            txt = f"➻ sᴛʀᴇᴀᴍ ʀᴇ-ᴘʟᴀʏᴇᴅ 🎄\n│ \n└ʙʏ : {mention} 🥀"
            db[chat_id][0]["played"] = 0
            
            img = await get_thumb(check[0]["vidid"], CallbackQuery.from_user.id, client) or \
                  (random.choice(STREAM_IMG_URL) if isinstance(STREAM_IMG_URL, list) else STREAM_IMG_URL)
            
            await Lucky.skip_stream(chat_id, check[0]["file"], video=True if check[0]["streamtype"]=="video" else False)
            
            run = await CallbackQuery.message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{check[0]['vidid']}", check[0]['title'][:23], check[0]['dur'], check[0]['by']),
                reply_markup=InlineKeyboardMarkup(stream_markup(_, chat_id)),
            )
            if chat_id in db and db[chat_id]:
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
            await CallbackQuery.edit_message_text(txt, reply_markup=close_markup(_))

    await CallbackQuery.answer()

# --- TIMER ---
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
    
