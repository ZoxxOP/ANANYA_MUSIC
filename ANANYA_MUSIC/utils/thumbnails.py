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


def circle_mask(size):
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, size, size), fill=255)
    return mask


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

        poster = Image.open(tmp).convert("RGBA")

    except Exception:
        traceback.print_exc()
        poster = Image.open(DEFAULT_IMG).convert("RGBA")
        title, channel, views, duration = "Now Playing", "", "", ""

    # ---------------- BACKGROUND ----------------
    bg = poster.resize((W, H)).filter(ImageFilter.GaussianBlur(40))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 130))
    canvas = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(canvas)

    # ---------------- GREEN BORDER ----------------
    green = (150, 255, 60)
    draw.rectangle((10, 10, W - 10, H - 10), outline=green, width=10)

    # ---------------- TOP LEFT TEXT ----------------
    draw.text(
        (28, 22),
        "AnanyaxMusic",
        fill=(255, 255, 255),
        font=font(FONT_BOLD, 28)
    )

    # ---------------- CIRCULAR POSTER ----------------
    size = 360
    poster = poster.resize((size, size))
    mask = circle_mask(size)

    px, py = 140, 200
    canvas.paste(poster, (px, py), mask)

    # circle border
    draw.ellipse(
        (px - 6, py - 6, px + size + 6, py + size + 6),
        outline=(120, 220, 200),
        width=6
    )

    # ---------------- FONTS ----------------
    f_head = font(FONT_BOLD, 46)
    f_title = font(FONT_BOLD, 34)
    f_meta = font(FONT_REG, 26)

    # ---------------- RIGHT TEXT ----------------
    tx = 560

    draw.text((tx, 190), "NOW PLAYING", fill=(255, 255, 255), font=f_head)

    draw.text(
        (tx, 255),
        title[:50],
        fill=(245, 245, 245),
        font=f_title
    )

    draw.text(
        (tx, 315),
        f"Views : {views} views",
        fill=(210, 210, 210),
        font=f_meta
    )

    draw.text(
        (tx, 355),
        f"Duration : {duration} Mins",
        fill=(210, 210, 210),
        font=f_meta
    )

    draw.text(
        (tx, 395),
        f"Channel : {channel}",
        fill=(210, 210, 210),
        font=f_meta
    )

    # ---------------- SAVE ----------------
    out = CACHE / f"{videoid}_final.png"
    canvas.save(out, quality=95, optimize=True)

    if tmp and tmp.exists():
        os.remove(tmp)

    return str(out)
