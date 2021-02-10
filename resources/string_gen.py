#!/usr/bin/env python3
# (c) https://t.me/TelethonChat/37677
# This Source Code Form is subject to the terms of the GNU
# General Public License, v.3.0. If a copy of the GPL was not distributed with this
# file, You can obtain one at https://www.gnu.org/licenses/gpl-3.0.en.html.

from telethon.sessions import StringSession
from telethon.sync import TelegramClient

ok = """  ____   ___ _____ 
         | __ ) / _ \_   _|
         |  _ \| | | || |  
         | |_) | |_| || |  
         |____/ \___/ |_|
"""
print(ok)
APP_ID = int(input("Enter APP ID here: \n"))
API_HASH = input("Enter API HASH here: \n")

with TelegramClient(StringSession(), APP_ID, API_HASH) as client:
    try:
        session = client.session.save()
        client.send_message("me", f"String Session \nTap To Copy. \n`{session}`")
        print("String Generated Sucessfully Check Your Saved Message.")
    except Exception as sed:
        print(f"Something Went Wrong While Generating String \nError : {sed}")
