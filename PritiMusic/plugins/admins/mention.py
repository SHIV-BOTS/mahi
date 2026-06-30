import asyncio
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram import filters

from PritiMusic import app
from PritiMusic.utils.istkhar_ban import admin_filter

SPAM_CHATS = []

@app.on_message(filters.command(["mention", "all"]) & filters.group & admin_filter)
async def tag_all_users(_, message):
    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        return await message.reply_text("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴛᴀɢ ᴀʟʟ**")

    # Prevent running multiple tag processes in the same chat
    if message.chat.id in SPAM_CHATS:
        return await message.reply_text("**❌ ᴛᴀɢɢɪɴɢ ɪs ᴀʟʀᴇᴀᴅʏ ɪɴ ᴘʀᴏɢʀᴇss...**")

    SPAM_CHATS.append(message.chat.id)
    usernum = 0
    usertxt = ""

    if replied:
        async for m in app.get_chat_members(message.chat.id):
            if message.chat.id not in SPAM_CHATS:
                break
            if m.user.is_bot or m.user.is_deleted:
                continue

            usernum += 1
            usertxt += f"⊚ [{m.user.first_name}](tg://user?id={m.user.id})\n"
            
            # Send batch of 5
            if usernum >= 5:
                await replied.reply_text(usertxt)
                await asyncio.sleep(2)
                usernum = 0
                usertxt = ""
        
        # Send remaining leftover users
        if usertxt and message.chat.id in SPAM_CHATS:
            await replied.reply_text(usertxt)

    else:
        text = message.text.split(None, 1)[1]
        async for m in app.get_chat_members(message.chat.id):
            if message.chat.id not in SPAM_CHATS:
                break
            if m.user.is_bot or m.user.is_deleted:
                continue

            usernum += 1
            usertxt += f"⊚ [{m.user.first_name}](tg://user?id={m.user.id})\n"
            
            # Send batch of 5
            if usernum >= 5:
                await app.send_message(message.chat.id, f"{text}\n\n{usertxt}")
                await asyncio.sleep(2)
                usernum = 0
                usertxt = ""
        
        # Send remaining leftover users
        if usertxt and message.chat.id in SPAM_CHATS:
            await app.send_message(message.chat.id, f"{text}\n\n{usertxt}")

    # Remove chat from list when done
    try:
        if message.chat.id in SPAM_CHATS:
            SPAM_CHATS.remove(message.chat.id)
    except Exception:
        pass


@app.on_message(filters.command(["alloff", "cancel"]) & filters.group & admin_filter)
async def cancelcmd(_, message):
    chat_id = message.chat.id
    if chat_id in SPAM_CHATS:
        try:
            SPAM_CHATS.remove(chat_id)
        except Exception:
            pass
        return await message.reply_text("**✅ ᴛᴀɢ ᴀʟʟ sᴜᴄᴄᴇssғᴜʟʟʏ sᴛᴏᴘᴘᴇᴅ!**")
    else:
        return await message.reply_text("**❌ ɴᴏ ᴛᴀɢɢɪɴɢ ᴘʀᴏᴄᴇss ɪs ᴏɴɢᴏɪɴɢ!**")
