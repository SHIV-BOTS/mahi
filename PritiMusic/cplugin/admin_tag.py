import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

# --- Global list to keep track of ongoing tagging ---
SPAM_CHATS = []

# ✅ 'client' parameter add kiya taaki har clone bot apna kaam khud kare
async def is_admin(client, chat_id, user_id):
    admin_ids = [
        admin.user.id
        async for admin in client.get_chat_members(
            chat_id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]
    return user_id in admin_ids


async def tag_all_admins(client, message):
    chat_id = message.chat.id
    if chat_id in SPAM_CHATS:
        return await message.reply_text(
            "**» ᴛᴀɢɢɪɴɢ ᴘʀᴏᴄᴇss ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴛᴏᴘ sᴏ ᴜsᴇ :-** `/cancel`"
        )

    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        await message.reply_text(
            "**ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴛᴀɢ ᴀʟʟ ᴀᴅᴍɪɴs, ʟɪᴋᴇ »** `@admin Hi Friends`"
        )
        return

    usernum = 0
    usertxt = ""
    text = message.text.split(None, 1)[1] if not replied and len(message.command) > 1 else ""

    try:
        SPAM_CHATS.append(chat_id)
        async for m in client.get_chat_members(
            chat_id, filter=ChatMembersFilter.ADMINISTRATORS
        ):
            if chat_id not in SPAM_CHATS:
                break
            if m.user.is_deleted or m.user.is_bot:
                continue
            usernum += 1
            usertxt += f"[{m.user.first_name}](tg://user?id={m.user.id})  "
            
            if usernum == 7:
                if replied:
                    await replied.reply_text(usertxt, disable_web_page_preview=True)
                else:
                    await client.send_message(
                        chat_id, f"{text}\n{usertxt}", disable_web_page_preview=True
                    )
                await asyncio.sleep(2)
                usernum = 0
                usertxt = ""
                
        if usernum != 0:
            if replied:
                await replied.reply_text(usertxt, disable_web_page_preview=True)
            else:
                await client.send_message(
                    chat_id, f"{text}\n\n{usertxt}", disable_web_page_preview=True
                )
    except FloodWait as e:
        await asyncio.sleep(e.value)
    finally:
        try:
            if chat_id in SPAM_CHATS:
                SPAM_CHATS.remove(chat_id)
        except Exception:
            pass


# ✅ Changed @app to @Client for clone bots
@Client.on_message(
    filters.command(["admin", "atag", "report"], prefixes=["/", "@"]) & filters.group
)
async def admintag_with_reporting(client, message):
    if not message.from_user:
        return
    
    chat_id = message.chat.id
    from_user_id = message.from_user.id
    
    admins = [
        admin.user.id
        async for admin in client.get_chat_members(
            chat_id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]

    if message.command[0] == "report" and from_user_id in admins:
        return await message.reply_text(
            "**» ᴏᴘᴘs! ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀᴅᴍɪɴ!**\n\n**ʏᴏᴜ ᴄᴀɴ'ᴛ ʀᴇᴘᴏʀᴛ ᴀɴʏ ᴜsᴇʀs ᴛᴏ ᴀᴅᴍɪɴ**"
        )

    if from_user_id in admins:
        return await tag_all_admins(client, message)

    if len(message.command) <= 1 and not message.reply_to_message:
        return await message.reply_text("**» ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʀᴇᴘᴏʀᴛ ᴛʜᴀᴛ ᴜsᴇʀ.**")

    reply = message.reply_to_message or message
    reply_user_id = reply.from_user.id if reply.from_user else reply.sender_chat.id
    
    # Safely get linked chat to prevent crashes
    try:
        chat_info = await client.get_chat(chat_id)
        linked_chat = chat_info.linked_chat
    except Exception:
        linked_chat = None

    # ✅ Fix: app.id ki jagah client.me.id use kiya
    if reply_user_id == client.me.id:
        return await message.reply_text("ᴡʜʏ ᴡᴏᴜʟᴅ ɪ ʀᴇᴘᴏʀᴛ ᴍʏsᴇʟғ?")
        
    if reply_user_id in admins or reply_user_id == chat_id or (linked_chat and reply_user_id == linked_chat.id):
        return await message.reply_text(
            "**» ᴅᴏ ʏᴏᴜ ᴋɴᴏᴡ ᴛʜᴀᴛ ᴛʜᴇ ᴜsᴇʀ ʏᴏᴜ ᴀʀᴇ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ɪs ᴀɴ ᴀᴅᴍɪɴ?**"
        )

    user_mention = reply.from_user.mention if reply.from_user else "ᴛʜᴇ ᴜsᴇʀ"
    text = f"**» ʀᴇᴘᴏʀᴛᴇᴅ {user_mention} ᴛᴏ ᴀᴅᴍɪɴs!.**"

    for admin in admins:
        try:
            admin_member = await client.get_chat_member(chat_id, admin)
            if not admin_member.user.is_bot and not admin_member.user.is_deleted:
                text += f"[\u2063](tg://user?id={admin})"
        except Exception:
            pass

    await reply.reply_text(text)


# ✅ Changed @app to @Client and added 'cancel' command too
@Client.on_message(
    filters.command(["stoptag", "astop", "cancel"], prefixes=["/", "@"]) & filters.group
)
async def cancelcmd(client, message):
    chat_id = message.chat.id
    admin = await is_admin(client, chat_id, message.from_user.id)
    
    if not admin:
        return
        
    if chat_id in SPAM_CHATS:
        try:
            SPAM_CHATS.remove(chat_id)
        except Exception:
            pass
        return await message.reply_text("**» ᴛᴀɢɢɪɴɢ ᴘʀᴏᴄᴇss sᴛᴏᴘᴘᴇᴅ!**")
    else:
        await message.reply_text("**» ɴᴏ ᴘʀᴏᴄᴇss ᴏɴɢᴏɪɴɢ!**")
        return
  
