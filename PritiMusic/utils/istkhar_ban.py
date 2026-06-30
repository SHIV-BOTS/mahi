from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid

from PritiMusic import app
from PritiMusic.utils.admin_check import admin_check

# --- Helper Function to Extract User ---
async def extract_user(client, message: Message):
    """Extracts user ID and first name from a reply or command argument."""
    user_id = None
    user_first_name = None

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name
    elif len(message.command) > 1:
        try:
            user = await client.get_users(message.command[1])
            user_id = user.id
            user_first_name = user.first_name
        except Exception:
            pass
            
    return user_id, user_first_name


# --- BAN COMMAND ---
@app.on_message(filters.command(["ban", "dban"]) & filters.group)
async def ban_user(client, message: Message):
    # 1. Check if the user sending the command is an admin
    is_admin = await admin_check(message)
    if not is_admin:
        return await message.reply_text("**❌ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ʙᴀɴ ᴜsᴇʀs.**")

    # 2. Extract the target user
    user_id, user_first_name = await extract_user(client, message)
    
    if not user_id:
        return await message.reply_text("**❌ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴛʜᴇɪʀ ᴜsᴇʀɴᴀᴍᴇ/ɪᴅ ᴛᴏ ʙᴀɴ ᴛʜᴇᴍ.**")

    # 3. Prevent the bot from banning itself
    if user_id == client.me.id:
        return await message.reply_text("**❌ ɪ ᴄᴀɴ'ᴛ ʙᴀɴ ᴍʏsᴇʟғ!**")

    # 4. Attempt to ban the user
    try:
        await client.ban_chat_member(message.chat.id, user_id)
        
        # If it's a dban (delete and ban), delete the replied message
        if message.command[0].lower() == "dban" and message.reply_to_message:
            await message.reply_to_message.delete()
            
        await message.reply_text(f"**✅ {user_first_name} ʜᴀs ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴛʜᴇ ᴄʜᴀᴛ!**")
        
    except ChatAdminRequired:
        await message.reply_text("**❌ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴅᴍɪɴ ʀɪɢʜᴛs ᴛᴏ ʙᴀɴ ᴜsᴇʀs. ᴘʟᴇᴀsᴇ ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ.**")
    except UserAdminInvalid:
        await message.reply_text("**❌ ɪ ᴄᴀɴ'ᴛ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ.**")
    except Exception as e:
        await message.reply_text(f"**❌ ᴇʀʀᴏʀ:** `{e}`")


# --- UNBAN COMMAND ---
@app.on_message(filters.command("unban") & filters.group)
async def unban_user(client, message: Message):
    # 1. Check if the user sending the command is an admin
    is_admin = await admin_check(message)
    if not is_admin:
        return await message.reply_text("**❌ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴜɴʙᴀɴ ᴜsᴇʀs.**")

    # 2. Extract the target user
    user_id, user_first_name = await extract_user(client, message)
    
    if not user_id:
        return await message.reply_text("**❌ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴛʜᴇɪʀ ᴜsᴇʀɴᴀᴍᴇ/ɪᴅ ᴛᴏ ᴜɴʙᴀɴ ᴛʜᴇᴍ.**")

    # 3. Attempt to unban the user
    try:
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text(f"**✅ {user_first_name} ʜᴀs ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ!**")
        
    except ChatAdminRequired:
        await message.reply_text("**❌ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴅᴍɪɴ ʀɪɢʜᴛs ᴛᴏ ᴜɴʙᴀɴ ᴜsᴇʀs. ᴘʟᴇᴀsᴇ ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ.**")
    except Exception as e:
        await message.reply_text(f"**❌ ᴇʀʀᴏʀ:** `{e}`")
