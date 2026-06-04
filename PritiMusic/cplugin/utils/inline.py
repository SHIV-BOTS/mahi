from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from button import styled_button, ButtonStyle # Zaroori import

# --- OPTION 1: Static ---
buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="▷", callback_data="resume_cb"),
            InlineKeyboardButton(text="II", callback_data="pause_cb"),
            InlineKeyboardButton(text="‣‣I", callback_data="skip_cb"),
            InlineKeyboardButton(text="▢", callback_data="end_cb"),
        ],
        [
            InlineKeyboardButton(text="『 ✦ 𝐂ʟᴏηє 𝐌є ✦ 』", url="https://t.me/clone_MUSICrobot")
        ],
    ]
)

close_key = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="『 ♡ 𝐀ᴅᴅ 𝐌є 𝐁ᴀʙʏ ♡ 』", url="https://t.me/clone_MUSICrobot?startgroup=true"),
            InlineKeyboardButton(text="✯ CLOSE ✯", callback_data="close")
        ]
    ]
)

# --- OPTION 2: Dynamic (RECOMMENDED) ---
def stream_markup(chat_id):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
                InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
                InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
                InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
            ],
            # --- NAYI ROW YAHAN ADD KI HAI ---
            [
                styled_button(text="<- 20s", callback_data=f"ADMIN SeekBack|{chat_id}", style=ButtonStyle.PRIMARY),
                styled_button(text="🔁", callback_data=f"ADMIN Loop|{chat_id}", style=ButtonStyle.PRIMARY),
                styled_button(text="🔀", callback_data=f"ADMIN Shuffle|{chat_id}", style=ButtonStyle.PRIMARY),
                styled_button(text="20s + ->", callback_data=f"ADMIN SeekForward|{chat_id}", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text="『 ✦ 𝐂ʟᴏηє 𝐌є ✦ 』", url="https://t.me/clone_MUSICrobot")
            ],
            [
                InlineKeyboardButton(text="『 ♡ 𝐀ᴅᴅ 𝐌є 𝐁ᴀʙʏ ♡ 』", url="https://t.me/clone_MUSICrobot?startgroup=true"),
                InlineKeyboardButton(text="✯ CLOSE ✯", callback_data="close")
            ]
        ]
    )
