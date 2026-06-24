import math, random
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from PritiMusic import app
from PritiMusic.utils.formatters import time_to_seconds

PREMIUM_EMOJIS = ["5422831825178206894", "5368324170673489600", "5206607081334906820", "5206380668048496464"]

def get_s(): return random.choice([ButtonStyle.PRIMARY, ButtonStyle.SUCCESS, ButtonStyle.DANGER])
def btn(text, cb=None, url=None, s=ButtonStyle.PRIMARY):
    k = {"text": text, "style": s}
    if cb: k["callback_data"] = cb
    if url: k["url"] = url
    return InlineKeyboardButton(**k)

def clone(s): return btn("『 ✦ 𝐂ʟᴏηє 𝐌є ✦ 』", url="https://t.me/SizzuMusicBot", style=s)

def stream_markup(_, chat_id):
    s = get_s()
    return InlineKeyboardMarkup([
        [btn("▷", f"ADMIN Resume|{chat_id}", s), btn("II", f"ADMIN Pause|{chat_id}", s), btn("↻", f"ADMIN Replay|{chat_id}", s), btn("‣‣I", f"ADMIN Skip|{chat_id}", s), btn("▢", f"ADMIN Stop|{chat_id}", s)],
        [btn("❖ 𝐀ᴜᴛᴏ𝐏ʟᴀʏ ❖", f"ADMIN Autoplay|{chat_id}", s), clone(s)]
    ])

def stream_markup_timer(_, chat_id, played, dur):
    bar = "▰" * int((time_to_seconds(played)/time_to_seconds(dur))*10) if time_to_seconds(dur)!=0 else ""
    return InlineKeyboardMarkup([[btn(f"{played} {bar} {dur}", "GetTimer", s=get_s())], *stream_markup(_, chat_id).inline_keyboard])

def track_markup(_, vid, uid, ch, f):
    s = get_s()
    return InlineKeyboardMarkup([[btn(_["P_B_1"], f"MusicStream {vid}|{uid}|a|{ch}|{f}", s), btn(_["P_B_2"], f"MusicStream {vid}|{uid}|v|{ch}|{f}", s)], [clone(s)]])

def playlist_markup(_, vid, uid, pt, ch, f):
    s = get_s()
    return InlineKeyboardMarkup([[btn(_["P_B_1"], f"LuckyPlaylists {vid}|{uid}|{pt}|a|{ch}|{f}", s), btn(_["P_B_2"], f"LuckyPlaylists {vid}|{uid}|{pt}|v|{ch}|{f}", s)], [clone(s)]])

def livestream_markup(_, vid, uid, mode, ch, f):
    s = get_s()
    return InlineKeyboardMarkup([[btn(_["P_B_3"], f"LiveStream {vid}|{uid}|{mode}|{ch}|{f}", s)], [clone(s)]])

def slider_markup(_, vid, uid, q, qt, ch, f):
    s = get_s()
    return InlineKeyboardMarkup([[btn(_["P_B_1"], f"MusicStream {vid}|{uid}|a|{ch}|{f}", s), btn(_["P_B_2"], f"MusicStream {vid}|{uid}|v|{ch}|{f}", s)], [btn("◁", f"slider B|{qt}|{q[:20]}|{uid}|{ch}|{f}", s), btn("▷", f"slider F|{qt}|{q[:20]}|{uid}|{ch}|{f}", s)], [clone(s)]])

def queue_markup(_, vid, cid):
    s = get_s()
    return InlineKeyboardMarkup([[btn(_["S_B_3"], url=f"https://t.me/{app.username}?startgroup=true", s=s)], *stream_markup(_, cid).inline_keyboard, [btn("ᴍᴏʀᴇ", f"PanelMarkup None|{cid}", s)]])

def panel_markup_clone(_, vid, cid, p, d):
    s = get_s()
    return InlineKeyboardMarkup([[btn(f"{p} {d}", "GetTimer", s=s)], *stream_markup(_, cid).inline_keyboard, [btn("<- 20s", f"ADMIN SeekBack|{cid}", s), btn("20s + ->", f"ADMIN SeekForward|{cid}", s)]])

def telegram_markup(_, cid): return InlineKeyboardMarkup([[btn("Next", f"PanelMarkup None|{cid}", get_s()), btn(_["CLOSEMENU_BUTTON"], "close", get_s())]])

def stream_markup2(_, cid): return stream_markup(_, cid)
def stream_markup_timer2(_, cid, p, d): return stream_markup_timer(_, cid, p, d)
def panel_markup_1(_, vid, cid): return queue_markup(_, vid, cid)
def panel_markup_2(_, vid, cid): return queue_markup(_, vid, cid)
def panel_markup_3(_, vid, cid): return queue_markup(_, vid, cid)
def panel_markup_5(_, vid, cid): return queue_markup(_, vid, cid)
def panel_markup_4(_, vid, cid, p, d): return panel_markup_clone(_, vid, cid, p, d)
    
