import os
import random
from logging import getLogger
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pyrogram import Client, filters, enums
from pyrogram.enums import ButtonStyle
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton

LOGGER = getLogger(__name__)

# --- Simple In-Memory Database ---
welcome_state = {}  # {chat_id: True/False}
last_welcome_msg = {}  # {chat_id: message_id}


# --- Image Processing Functions ---
def create_circular_pfp(pfp, size=(500, 500), brightness=1.3):
    pfp = pfp.resize(size, Image.Resampling.LANCZOS).convert("RGBA")
    pfp = ImageEnhance.Brightness(pfp).enhance(brightness)
    
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    
    pfp.putalpha(mask)
    return pfp

def generate_welcome_image(pic_path, user_id):
    bg_path = "assets/wel2.png"
    font_path = "assets/font.ttf"
    
    if not os.path.exists(bg_path):
        LOGGER.warning("Background image 'wel2.png' not found in 'assets' folder.")
        return None

    background = Image.open(bg_path).convert("RGBA")
    
    try:
        pfp = Image.open(pic_path).convert("RGBA")
    except Exception:
        if os.path.exists("assets/upic.png"):
            pfp = Image.open("assets/upic.png").convert("RGBA") 
        else:
            pfp = Image.new("RGBA", (500, 500), (255, 255, 255, 0)) 
        
    pfp = create_circular_pfp(pfp)
    draw = ImageDraw.Draw(background)
    
    try:
        font = ImageFont.truetype(font_path, size=60)
    except Exception:
        font = ImageFont.load_default()
        
    draw.text((630, 450), f'ID: {user_id}', fill=(255, 255, 255), font=font)
    background.paste(pfp, (48, 88), pfp)
    
    os.makedirs("downloads", exist_ok=True)
    output_path = f"downloads/welcome_{user_id}.png"
    background.save(output_path)
    return output_path


# --- Welcome Toggle Command ---
# Yahan @app ki jagah @Client use kiya hai taaki clone bots command sune
@Client.on_message(filters.command("welcome") & filters.group)
async def toggle_welcome(client: Client, message):
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        return await message.reply("**sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇɴᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ!**")

    if len(message.command) != 2 or message.command[1].lower() not in ["on", "off"]:
        return await message.reply("**ᴜsᴀɢᴇ:**\n**⦿ /welcome [on|off]**")

    state = message.command[1].lower()
    chat_id = message.chat.id

    if state == "on":
        welcome_state[chat_id] = True
        await message.reply(f"**ᴇɴᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ {message.chat.title}**")
    else:
        welcome_state[chat_id] = False
        await message.reply(f"**ᴅɪsᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ {message.chat.title}**")


# --- Welcome Event Handler ---
# Yahan bhi @app ki jagah @Client use kiya hai
@Client.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(client: Client, member: ChatMemberUpdated):
    chat_id = member.chat.id
    
    if welcome_state.get(chat_id, True) == False:
        return

    if not (member.new_chat_member and not member.old_chat_member and member.new_chat_member.status != enums.ChatMemberStatus.BANNED):
        return

    user = member.new_chat_member.user
    count = await client.get_chat_members_count(chat_id)

    if chat_id in last_welcome_msg:
        try:
            await last_welcome_msg[chat_id].delete()
        except Exception:
            pass

    try:
        pic_path = "assets/upic.png"
        if user.photo:
            try:
                os.makedirs("downloads", exist_ok=True)
                pic_path = await client.download_media(user.photo.big_file_id, file_name=f"downloads/pp{user.id}.png")
            except Exception:
                pass

        welcome_img = generate_welcome_image(pic_path, user.id)
        
        # Clone bot ka khud ka username nikalne ka code
        bot_info = await client.get_me()
        bot_username = bot_info.username
        
        caption = f"""
**⎊─────☵ ᴡᴇʟᴄᴏᴍᴇ ☵─────⎊**

**▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬**

**☉ ɴᴀᴍᴇ ⧽** {user.mention}
**☉ ɪᴅ ⧽** `{user.id}`
**☉ ᴜ_ɴᴀᴍᴇ ⧽** @{user.username or "None"}
**☉ ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs ⧽** {count}

**▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬**

**⎉──────▢✭ 侖 ✭▢──────⎉**
"""
        styles = [ButtonStyle.PRIMARY, ButtonStyle.SUCCESS, ButtonStyle.DANGER]

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("๏ ᴠɪᴇᴡ ɴᴇᴡ ᴍᴇᴍʙᴇʀ ๏", url=f"tg://openmessage?user_id={user.id}", style=random.choice(styles))],
            [InlineKeyboardButton("✙ ᴋɪᴅɴᴀᴘ ᴍᴇ ✙", url=f"https://t.me/{bot_username}?startgroup=true", style=random.choice(styles))],
        ])

        if welcome_img:
            msg = await client.send_photo(chat_id, photo=welcome_img, caption=caption, reply_markup=markup)
        else:
            msg = await client.send_message(chat_id, text=caption, reply_markup=markup)

        last_welcome_msg[chat_id] = msg
        
        # Files Cleanup
        if welcome_img and os.path.exists(welcome_img):
            os.remove(welcome_img)
        if pic_path and os.path.exists(pic_path) and "assets" not in pic_path:
            os.remove(pic_path)

    except Exception as e:
        LOGGER.error(f"Welcome Error: {e}")
  
