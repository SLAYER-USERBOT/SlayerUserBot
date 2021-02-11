#    Copyright (C) Midhun KM 2020-2021
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from slayerbot.Configs import Config
import time
from telethon import __version__ as tv
import sys
import platform
from git import Repo
from slayerbot import ALIVE_NAME
from slayerbot.modules import currentversion

DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else "Unknown"
PM_IMG = "https://telegra.ph/file/60569be50266114d5e44e.jpg"
pm_caption = "➥ **ASSISTANT IS:** `ONLINE`\n\n"
pm_caption += "➥ **SYSTEMS STATS**\n"
pm_caption += f"➥ **Telethon Version:** `{tv}` \n"
pm_caption += f"➥ **Python:** `{platform.python_version()}` \n"
pm_caption += "➥ **Database Status:**  `Functional`\n"
pm_caption += "➥ **Current Branch** : `master`\n"
pm_caption += f"➥ **Version** : `{currentversion}`\n"
pm_caption += f"➥ **My Boss** : {DEFAULTUSER} \n"
pm_caption += "➥ **Heroku Database** : `AWS - Working Properly`\n\n"
pm_caption += "➥ **License** : [GNU General Public License v3.0](github.com/SLAYER-USERBOT/SlayerUserbot/blob/master/LICENSE)\n"
pm_caption += "➥ **Copyright** : By [OWNER](https://t.me/Slayer_UserBot)\n"
pm_caption += "[Assistant By Slayer 🇮🇳](https://t.me/Slayer_UserBot)"

# only Owner Can Use it
@assistant_cmd("alive", is_args=False)
@peru_only
async def slayer(event):
    await tgbot.send_file(event.chat_id, PM_IMG, caption=pm_caption)
