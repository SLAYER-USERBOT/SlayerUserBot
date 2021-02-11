# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
"""
Userbot module to help you manage a group
"""

from asyncio import sleep
from os import remove
from fridaybot.function import is_admin
from telethon.errors import (
    BadRequestError,
    ChatAdminRequiredError,
    ImageProcessFailedError,
    PhotoCropSizeSmallError,
    UserAdminInvalidError,
)
from telethon.errors.rpcerrorlist import MessageTooLongError, UserIdInvalidError
from telethon.tl.functions.channels import (
    EditAdminRequest,
    EditBannedRequest,
    EditPhotoRequest,
)
from telethon.tl.functions.messages import UpdatePinnedMessageRequest
from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChatAdminRights,
    ChatBannedRights,
    MessageEntityMentionName,
    MessageMediaPhoto,
)

from fridaybot import BOTLOG, BOTLOG_CHATID, CMD_HELP
from fridaybot.utils import edit_or_reply, friday_on_cmd, sudo_cmd

# =================== CONSTANT ===================
PP_TOO_SMOL = "`The image is too small`"
PP_ERROR = "`Failure while processing the image`"
NO_ADMIN = "`I am not an admin nub nibba!`"
NO_PERM = (
    "`I don't have sufficient permissions! This is so sed. Alexa play Tera Baap Aaya`"
)
NO_SQL = "`Running on Non-SQL mode!`"

CHAT_PP_CHANGED = "`Chat Picture Changed`"
CHAT_PP_ERROR = (
    "`Some issue with updating the pic,`"
    "`maybe coz I'm not an admin,`"
    "`or don't have enough rights.`"
)
INVALID_MEDIA = "`Invalid Extension`"

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)

UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)
# ================================================



# ------------------------------------------------------------------------------------
async def get_user_from_event(event):
    args = event.pattern_match.group(1).split(" ", 1)
    extra = None
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.sender_id)
        extra = event.pattern_match.group(1)
    elif args:
        user = args[0]
        if len(args) == 2:
            extra = args[1]
        if user.isnumeric():
            user = int(user)
        if not user:
            await event.edit("`Pass the User's Username, ID or Reply!`")
            return None, None
        if event.message.entities:
            probable_user_mention_entity = event.message.entities[0]
            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj, extra
        try:
            user_obj = await event.client.get_entity(user)
        except (TypeError, ValueError):
            return None, None
    return user_obj, extra


async def get_user_sender_id(user, event):
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await event.client.get_entity(user)
    except (TypeError, ValueError) as err:
        await event.edit(str(err))
        return None

    return user_obj
# --------------------------------------------------------------------------------------------


# @register(outgoing=True, pattern="^.setevent$")
@friday.on(friday_on_cmd(pattern="setgpic$"))
@friday.on(sudo_cmd(pattern="setgpic$", allow_sudo=True))
async def set_group_photo(event):
    if event.fwd_from:
        return
    """ For .setevent command, changes the picture of a group """
    if not event.is_group:
        poppo = await edit_or_reply(event, "`I don't think this is a group.`")
        return
    replyevent = await event.get_reply_message()
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    photo = None
    if not admin and not creator:
        poppo = await edit_or_reply(event, NO_ADMIN)
        return
    if replyevent and replyevent.media:
        if isinstance(replyevent.media, MessageMediaPhoto):
            photo = await event.client.download_media(message=replyevent.photo)
        elif "image" in replyevent.media.document.mime_type.split("/"):
            photo = await event.client.download_file(replyevent.media.document)
        else:
            poppo = await edit_or_reply(event, INVALID_MEDIA)

    if photo:
        try:
            await event.client(
                EditPhotoRequest(event.chat_id, await event.client.upload_file(photo))
            )
            poppo = await edit_or_reply(event, CHAT_PP_CHANGED)

        except PhotoCropSizeSmallError:
            poppo = await edit_or_reply(event, PP_TOO_SMOL)
        except ImageProcessFailedError:
            poppo = await edit_or_reply(event, PP_ERROR)


# @register(outgoing=True, pattern="^.promote(?: |$)(.*)")
@friday.on(friday_on_cmd(pattern="promote(?: |$)(.*)"))
@friday.on(sudo_cmd(pattern="promote(?: |$)(.*)", allow_sudo=True))
async def promote(event):
    if event.fwd_from:
        return
    if not event.is_group:
        poppo = await edit_or_reply(event, "`I don't think this is a group.`")
        return
    """ For .promote command, promotes the replied/tagged person """
    # Get targeted chat
    chat = await event.get_chat()
    # Grab admin status or creator in a chat
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, also return
    if not admin and not creator:
        poppo = await edit_or_reply(event, NO_ADMIN)
        return

    new_rights = ChatAdminRights(
        add_admins=False,
        invite_users=True,
        change_info=False,
        ban_users=True,
        delete_messages=True,
        pin_messages=True,
    )

    poppo = await edit_or_reply(event, "`Promoting...`")
    user, rank = await get_user_from_event(event)
    if not rank:
        rank = "admeme"  # Just in case.
    if user:
        pass
    else:
        return

    # Try to promote if current user is admin or creator
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
        await poppo.edit(f"Sucessfully, Promoted [{user.first_name}](tg://user?id={user.id}) in {event.chat.title}")

    # If Telethon spit BadRequestError, assume
    # we don't have Promote permission
    except BadRequestError:
        await poppo.edit(NO_PERM)
        return
    # Announce to the logging group if we have promoted successfully
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "#PROMOTE\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {event.chat.title}(`{event.chat_id}`)",
        )


# @register(outgoing=True, pattern="^.demote(?: |$)(.*)")
@friday.on(friday_on_cmd(pattern="demote(?: |$)(.*)"))
@friday.on(sudo_cmd(pattern="demote(?: |$)(.*)", allow_sudo=True))
async def demote(event):
    if event.fwd_from:
        return
    if not event.is_group:
        poppo = await edit_or_reply(event, "`I don't think this is a group.`")
        return
    """ For .demote command, demotes the replied/tagged person """
    # Admin right check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        poppo = await edit_or_reply(event, NO_ADMIN)
        return

    # If passing, declare that we're going to demote
    poppo = await edit_or_reply(event, "`Demoting...`")
    rank = "admeme"  # dummy rank, lol.
    user, reason = await get_user_from_event(event)
    if user:
        pass
    else:
        return
    # New rights after demotion
    newrights = ChatAdminRights(
        add_admins=None,
        invite_users=None,
        change_info=None,
        ban_users=None,
        delete_messages=None,
        pin_messages=None,
    )
    # Edit Admin Permission
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, newrights, rank))

    # If we catch BadRequestError from Telethon
    # Assume we don't have permission to demote
    except BadRequestError:
        popp9 = await edit_or_reply(event, NO_PERM)
        return
    await poppo.edit(f"Demoted, [{user.first_name}](tg://user?id={user.id}) in {event.chat.title} Sucessfully!")

    # Announce to the logging group if we have demoted successfully
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "#DEMOTE\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {event.chat.title}(`{event.chat_id}`)",
        )


# @register(outgoing=True, pattern="^.ban(?: |$)(.*)")
@friday.on(friday_on_cmd(pattern="ban(?: |$)(.*)"))
@friday.on(sudo_cmd(pattern="ban(?: |$)(.*)", allow_sudo=True))
async def ban(event):
    if event.fwd_from:
        return
    if not event.is_group:
        poppo = await edit_or_reply(event, "`I don't think this is a group.`")
        return
    """ For .ban command, bans the replied/tagged person """
    # Here laying the sanity check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not admin and not creator:
        poppo = await edit_or_reply(event, NO_ADMIN)
        return

    user, reason = await get_user_from_event(event)
    if user:
        pass
    else:
        return

    # Announce that we're going to whack the pest
    poppo = await edit_or_reply(event, "`Dusting Dust of ban Hammer`")

    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
    except BadRequestError:
        await poppo.edit(NO_PERM)
        return
    # Helps ban group join spammers more easily
    try:
        reply = await event.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        poppio = await edit_or_reply(event, "`I dont have message nuking rights! But still he was banned!`")
        return
    # Delete message and then tell that the command
    # is done gracefully
    # Shout out the ID, so that fedadmins can fban later
    if reason:
        await poppo.edit(f"Sucessfully, Banned [{user.first_name}](tg://user?id={user.id}) in {event.chat.title} For Reason: {reason}")
    else:
        await poppo.edit(f"Sucessfully, Banned [{user.first_name}](tg://user?id={user.id}) in {event.chat.title}")
    # Announce to the logging group if we have banned the person
    # successfully!
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "#BAN\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {event.chat.title}(`{event.chat_id}`)",
        )


# @register(outgoing=True, pattern="^.unban(?: |$)(.*)")
@friday.on(friday_on_cmd(pattern="unban(?: |$)(.*)"))
@friday.on(sudo_cmd(pattern="unban(?: |$)(.*)", allow_sudo=True))
async def nothanos(event):
    if event.fwd_from:
        return
    if not event.is_group:
        poppo = await edit_or_reply(event, "`I don't think this is a group.`")
        return
    """ For .unban command, unbans the replied/tagged person """
    # Here laying the sanity check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not admin and not creator:
        poppo = await edit_or_reply(event, NO_ADMIN)
        return

    # If everything goes well...
    poppo = await edit_or_reply(event, "`Unbanning...`")

    user = await get_user_from_event(event)
    user = user[0]
    if user:
        pass
    else:
        return

    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
        await poppo.edit(f"Sucessfully, UnBanned, [{user.first_name}](tg://user?id={user.id}) in {event.chat.title}")

        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#UNBAN\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {event.chat.title}(`{event.chat_id}`)",
            )
    except UserIdInvalidError:
        await poppo.edit("`Uh oh my unban logic broke!`")


@friday.on(friday_on_cmd(pattern=r"mute(?: |$)(.*)"))
async def spider(event):
    if event.fwd_from:
        return
    if not event.is_group:
        poppo = await edit_or_reply(event, "`I don't think this is a group.`")
        return
    """
    This function is basically muting peeps
    """
    # Check if the function running under SQL mode
    try:
        from userbot.modules.sql_helper.spam_mute_sql import mute
    except AttributeError:
        poppo = await edit_or_reply(event, NO_SQL)
        return

    # Admin or creator check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        poppo = await edit_or_reply(event, NO_ADMIN)
        return

    user, reason = await get_user_from_event(event)
    if user:
        pass
    else:
        return

    self_user = await event.client.get_me()

    if user.id == self_user.id:
        poppo = await edit_or_reply(event, "`Hands too short, can't duct tape myself...\n(ヘ･_･)ヘ┳━┳`")
        return

    # If everything goes well, do announcing and mute
    poppo = await edit_or_reply(event, "`Gets a tape!`")
    if mute(event.chat_id, user.id) is False:
        return await poppo.edit("`Error! User probably already muted.`")
    else:
        try:
            await event.client(EditBannedRequest(event.chat_id, user.id, MUTE_RIGHTS))

            # Announce that the function is done
            if reason:
                await poppo.edit(f"`Safely taped !!`\nReason: {reason}")
            else:
                await poppo.edit("`Safely taped !!`")

            # Announce to logging group
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#MUTE\n"
                    f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                    f"CHAT: {event.chat.title}(`{event.chat_id}`)",
                )
        except UserIdInvalidError:
            return await event.edit("`Uh oh my mute logic broke!`")


# @register(outgoing=True, pattern="^.unmute(?: |$)(.*)")
@friday.on(friday_on_cmd(pattern="unmute(?: |$)(.*)"))
@friday.on(sudo_cmd(pattern="unmute(?: |$)(.*)", allow_sudo=True))
async def unmoot(event):
    if event.fwd_from:
        return
    if not event.is_group:
        poppo = await edit_or_reply(event, "`I don't think this is a group.`")
        return
    """ For .unmute command, unmute the replied/tagged person """
    # Admin or creator check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        poppo = await edit_or_reply(event, NO_ADMIN)
        return

    # Check if the function running under SQL mode
    try:
        from userbot.modules.sql_helper.spam_mute_sql import unmute
    except AttributeError:
        poppo = await edit_or_reply(event, NO_SQL)
        return

    # If admin or creator, inform the user and start unmuting
    poppo = await edit_or_reply(event, "```Unmuting...```")
    user = await get_user_from_event(event)
    user = user[0]
    if user:
        pass
    else:
        return

    if unmute(event.chat_id, user.id) is False:
        return await poppo.edit("`Error! User probably already unmuted.`")
    else:

        try:
            await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
            await poppo.edit("```Unmuted Successfully```")
        except UserIdInvalidError:
            await poppo.edit("`Uh oh my unmute logic broke!`")
            return

        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#UNMUTE\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {event.chat.title}(`{event.chat_id}`)",
            )


# @register(outgoing=True, pattern="^.adminlist$")
@friday.on(friday_on_cmd(pattern="adminlist$"))
@friday.on(sudo_cmd(pattern="adminlist$", allow_sudo=True))
async def get_admin(event):
    if event.fwd_from:
        return
    if not event.is_group:
        poppo = await edit_or_reply(event, "`I don't think this is a group.`")
        return
    """ For .admins command, list all of the admins of the chat. """
    poppo = await edit_or_reply(event, "processing...")
    info = await event.client.get_entity(event.chat_id)
    title = info.title if info.title else "this chat"
    mentions = f"<b>Admins in {title}:</b> \n"
    try:
        async for user in event.client.iter_participants(
            event.chat_id, filter=ChannelParticipantsAdmins
        ):
            if not user.deleted:
                link = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
                userid = f"<code>{user.id}</code>"
                mentions += f"\n{link} {userid}"
            else:
                mentions += f"\nDeleted Account <code>{user.id}</code>"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    await poppo.edit(mentions, parse_mode="html")


# @register(outgoing=True, pattern="^.pin(?: |$)(.*)")
@friday.on(friday_on_cmd(pattern="pin(?: |$)(.*)"))
@friday.on(sudo_cmd(pattern="pin(?: |$)(.*)", allow_sudo=True))
async def pin(event):
    if event.fwd_from:
        return
    """ For .pin command, pins the replied/tagged message on the top the chat. """
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    # If not admin and not creator, return
    if not admin and not creator:
        poppo = await edit_or_reply(event, NO_ADMIN)
        return
    to_pin = event.reply_to_msg_id

    if not to_pin:
        poppo = await edit_or_reply(event, "`Reply to a message to pin it.`")
        return

    options = event.pattern_match.group(1)

    is_silent = True

    if options.lower() == "loud":
        is_silent = False

    try:
        await event.client(UpdatePinnedMessageRequest(event.to_id, to_pin, is_silent))
    except BadRequestError:
        poppo = await edit_or_reply(event, NO_PERM)
        return
    h = str(event.chat_id).replace("-100", "")
    poppo = await edit_or_reply(event, f"I Have Pinned This [Message](http://t.me/c/{h}/{to_pin})")
    user = await get_user_sender_id(event.sender_id, event)

    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "#PIN\n"
            f"ADMIN: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {event.chat.title}(`{event.chat_id}`)\n"
            f"LOUD: {not is_silent}",
        )


# @register(outgoing=True, pattern="^.kick(?: |$)(.*)")
@friday.on(friday_on_cmd(pattern="kick(?: |$)(.*)"))
@friday.on(sudo_cmd(pattern="kick(?: |$)(.*)", allow_sudo=True))
async def kick(event):
    if event.fwd_from:
        return
    if not event.is_group:
        poppo = await edit_or_reply(event, "`I don't think this is a group.`")
        return
    """ For .kick command, kicks the replied/tagged person from the group. """
    # Admin or creator check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        poppo = await edit_or_reply(event, NO_ADMIN)
        return

    user, reason = await get_user_from_event(event)
    if not user:
        poppo = await edit_or_reply(event, "`Couldn't fetch user.`")
        return

    poppo = await edit_or_reply(event, "`Kicking...`")

    try:
        await event.client.kick_participant(event.chat_id, user.id)
        await sleep(0.5)
    except Exception as e:
        await poppo.edit(NO_PERM + f"\n{str(e)}")
        return

    if reason:
        await poppo.edit(
            f"I Have Kicked [{user.first_name}](tg://user?id={user.id}) from {event.chat.title} For Reason : {reason}"
        )
    else:
        await poppo.edit(f"Kicked [{user.first_name}](tg://user?id={user.id}) from {event.chat.title}")

    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "#KICK\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {event.chat.title}(`{event.chat_id}`)\n",
        )


# @register(outgoing=True, pattern="^.users ?(.*)")
@friday.on(friday_on_cmd(pattern="users ?(.*)"))
@friday.on(sudo_cmd(pattern="users ?(.*)", allow_sudo=True))
async def get_users(event):
    if event.fwd_from:
        return
    if not event.is_group:
        poppo = await edit_or_reply(event, "`I don't think this is a group.`")
        return
    """ For .users command, list all of the users in a chat. """
    info = await event.client.get_entity(event.chat_id)
    title = info.title if info.title else "this chat"
    mentions = "Users in {}: \n".format(title)
    try:
        if not event.pattern_match.group(1):
            async for user in event.client.iter_participants(event.chat_id):
                if not user.deleted:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                    )
                else:
                    mentions += f"\nDeleted Account `{user.id}`"
        else:
            searchq = event.pattern_match.group(1)
            async for user in event.client.iter_participants(
                event.chat_id, search=f"{searchq}"
            ):
                if not user.deleted:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                    )
                else:
                    mentions += f"\nDeleted Account `{user.id}`"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    try:
        poppo = await edit_or_reply(event, mentions)
    except MessageTooLongError:
        poppo = await edit_or_reply(event, "Damn, this is a huge group. Uploading users lists as file.")
        file = open("userslist.txt", "w+")
        file.write(mentions)
        file.close()
        await event.client.send_file(
            event.chat_id,
            "userslist.txt",
            caption="Users in {}".format(title),
            reply_to=event.id,
        )
        remove("userslist.txt")

@friday.on(friday_on_cmd(pattern="zombies(?: |$)(.*)"))
@friday.on(sudo_cmd(pattern="zombies(?: |$)(.*)", allow_sudo=True))
async def rm_deletedacc(event):
    if event.fwd_from:
        return
    if not event.is_group:
        poppo = await edit_or_reply(event, "`I don't think this is a group.`")
        return
    con = event.pattern_match.group(1).lower()
    del_u = 0
    del_status = "`No deleted accounts found, Group is clean`"
    if con != "clean":
        poppo = await edit_or_reply(event, "`Searching for ghost/deleted/zombie accounts...`")
        async for user in event.client.iter_participants(event.chat_id):

            if user.deleted:
                del_u += 1
                await sleep(1)
        if del_u > 0:
            del_status = f"Found **{del_u}** ghost/deleted/zombie account(s) in this group,\
            \nclean them by using `.zombies clean`"

        poppo = await edit_or_reply(event, del_status)
        return
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        poppo = await edit_or_reply(event, "`I am not an admin here!`")
        return
    poppo = await edit_or_reply(event, "`Deleting deleted accounts...\nOh I can do that?!?!`")
    del_u = 0
    del_a = 0
    async for user in event.client.iter_participants(event.chat_id):
        if user.deleted:
            try:
                await poppo.client(
                    EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS)
                )
            except ChatAdminRequiredError:
                await poppo.edit("`I don't have ban rights in this group`")
                return
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
            del_u += 1
    if del_u > 0:
        del_status = f"Cleaned **{del_u}** deleted account(s)"
    if del_a > 0:
        del_status = f"Cleaned **{del_u}** deleted account(s) \
        \n**{del_a}** deleted admin accounts are not removed"

    await poppo.edit(del_status)
    await sleep(2)
    await poppo.delete()




CMD_HELP.update(
    {
        "admin": ".promote <username/reply> <custom rank (optional)>\
\n**Usage:** Provides admin rights to the person in the chat.\
\n\n.demote <username/reply>\
\n**Usage:** Revokes the person's admin permissions in the chat.\
\n\n.ban <username/reply> <reason (optional)>\
\n**Usage:** Bans the person off your chat.\
\n\n.unban <username/reply>\
\n**Usage:** Removes the ban from the person in the chat.\
\n\n.mute <username/reply> <reason (optional)>\
\n**Usage:** Mutes the person in the chat, works on admins too.\
\n\n.unmute <username/reply>\
\n**Usage:** Removes the person from the muted list.\
\n\n.gmute <username/reply> <reason (optional)>\
\n**Usage:** Mutes the person in all groups you have in common with them.\
\n\n.ungmute <username/reply>\
\n**Usage:** Reply someone's message with .ungmute to remove them from the gmuted list.\
\n\n.zombies\
\n**Usage:** Searches for deleted accounts in a group. Use .zombies clean to remove deleted accounts from the group.\
\n\n.adminlist\
\n**Usage:** Retrieves a list of admins in the chat.\
\n\n.users or .users <name of member>\
\n**Usage:** Retrieves all (or queried) users in the chat.\
\n\n.setgppic <reply to image>\
\n**Usage:** Changes the group's display picture."
    }
)
