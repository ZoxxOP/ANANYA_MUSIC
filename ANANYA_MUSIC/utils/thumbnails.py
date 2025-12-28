import os
from pathlib import Path
import traceback

import aiohttp
import aiofiles
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from py_yt import VideosSearch

# ---------------- CONFIG ----------------
CACHE = Path("cache")
CACHE.mkdir(exist_ok=True)

W, H = 1280, 720

FONT_BOLD = "ANANYA_MUSIC/assets/font.ttf"
FONT_REG = "ANANYA_MUSIC/assets/font2.ttf"
DEFAULT_IMG = "ANANYA_MUSIC/assets/AnanyaBots.jpg"


# ---------------- HELPERS ----------------
def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()


# ---------------- MAIN ----------------
async def get_thumb(videoid: str):
    tmp = None

    try:
        data = (await VideosSearch(
            f"https://www.youtube.com/watch?v={videoid}", limit=1
        ).next())["result"][0]

        title = data["title"]
        channel = data["channel"]["name"]
        views = data["viewCount"]["short"]
        duration = data["duration"]

        thumb = data["thumbnails"][-1]["url"].split("?")[0]
        tmp = CACHE / f"{videoid}.jpg"

        async with aiohttp.ClientSession() as s:
            async with s.get(thumb) as r:
                async with aiofiles.open(tmp, "wb") as f:
                    await f.write(await r.read())

        cover = Image.open(tmp).convert("RGBA")

    except Exception:
        traceback.print_exc()
        cover = Image.open(DEFAULT_IMG).convert("RGBA")
        title, channel, views, duration = "Pal Pal Loop", "Unknown", "0", "00:00"

    # ---------------- BACKGROUND ----------------
    bg = cover.resize((W, H)).filter(ImageFilter.GaussianBlur(35))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 160))
    canvas = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(canvas)

    # ---------------- TOP LEFT CORNER TEXT ----------------
    f_corner = font(FONT_REG, 22)
    draw.text(
        (18, 14),
        "TheAnanya",
        fill=(200, 200, 200),
        font=f_corner
    )

    # ---------------- LEFT CARD FRAME ----------------
    card_x, card_y = 90, 90
    card_w, card_h = 420, 540
    pink = (235, 170, 210)

    draw.rounded_rectangle(
        (card_x - 12, card_y - 12, card_x + card_w + 12, card_y + card_h + 12),
        radius=40,
        outline=pink,
        width=8
    )

    # ---------------- COVER IMAGE ----------------
    cover = cover.resize((360, 360))
    mask = Image.new("L", (360, 360), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 360, 360), 25, fill=255)
    canvas.paste(cover, (card_x + 30, card_y + 25), mask)

    # ---------------- PROGRESS BAR (LEFT) ----------------
    bar_y = card_y + 410
    draw.line(
        (card_x + 40, bar_y, card_x + 380, bar_y),
        fill=(120, 120, 120),
        width=6
    )
    draw.line(
        (card_x + 40, bar_y, card_x + 200, bar_y),
        fill=pink,
        width=6
    )

    f_small = font(FONT_REG, 18)
    draw.text((card_x + 40, bar_y + 12), "00:00", fill=(180, 180, 180), font=f_small)
    draw.text((card_x + 330, bar_y + 12), duration, fill=(180, 180, 180), font=f_small)

    # ---------------- TEXT BELOW COVER ----------------
    f_title = font(FONT_BOLD, 24)
    f_meta = font(FONT_REG, 18)

    draw.text(
        (card_x + 40, card_y + 450),
        title[:26],
        fill=(245, 245, 245),
        font=f_title
    )

    draw.text(
        (card_x + 40, card_y + 480),
        f"{channel} | {views} views",
        fill=(170, 170, 170),
        font=f_meta
    )

    # ---------------- RIGHT SIDE INFO ----------------
    f_np = font(FONT_REG, 20)
    f_big = font(FONT_BOLD, 46)
    f_info = font(FONT_REG, 28)

    # NOW PLAYING pill
    pill_x, pill_y = 560, 140
    draw.rounded_rectangle(
        (pill_x, pill_y, pill_x + 150, pill_y + 40),
        radius=20,
        fill=pink
    )
    draw.text(
        (pill_x + 22, pill_y + 9),
        "NOW PLAYING",
        fill=(0, 0, 0),
        font=f_np
    )

    # TITLE
    draw.text(
        (560, 200),
        title,
        fill=(255, 255, 255),
        font=f_big
    )

    # underline
    draw.line((560, 260, 980, 260), fill=pink, width=3)

    # META
    draw.text((560, 300), "Duration:", fill=(200, 200, 200), font=f_info)
    draw.text((700, 300), duration, fill=pink, font=f_info)

    draw.text((560, 345), "Views:", fill=(200, 200, 200), font=f_info)
    draw.text((700, 345), views, fill=pink, font=f_info)

    # ---------------- RIGHT PROGRESS ----------------
    bar_y2 = 420
    draw.line((560, bar_y2, 1040, bar_y2), fill=(140, 140, 140), width=6)
    draw.line((560, bar_y2, 800, bar_y2), fill=(255, 255, 255), width=6)
    draw.ellipse((790, bar_y2 - 6, 806, bar_y2 + 10), fill=(255, 255, 255))

    draw.text((560, bar_y2 + 12), "00:00", fill=(180, 180, 180), font=f_small)
    draw.text((1000, bar_y2 + 12), duration, fill=(180, 180, 180), font=f_small)

    # ---------------- SAVE ----------------
    out = CACHE / f"{videoid}_final.png"
    canvas.save(out, quality=95)

    if tmp and tmp.exists():
        os.remove(tmp)

    return str(out)
