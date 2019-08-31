# SCP-079-CLEAN - Filter specific types of messages
# Copyright (C) 2019 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-CLEAN.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import re
from typing import Union

from pyrogram import Client, Filters, Message

from .. import glovar
from .channel import get_content
from .etc import get_channel_link, get_command_type, get_entity_text, get_now, get_links, get_stripped_link, get_text
from .file import delete_file, get_downloaded_path, save
from .ids import init_group_id
from .image import get_file_id, get_qrcode
from .telegram import resolve_username

# Enable logging
logger = logging.getLogger(__name__)


def is_class_c(_, message: Message) -> bool:
    # Check if the message is Class C object
    try:
        if message.from_user:
            uid = message.from_user.id
            gid = message.chat.id
            if init_group_id(gid):
                if uid in glovar.admin_ids.get(gid, set()) or uid in glovar.bot_ids or message.from_user.is_self:
                    return True
    except Exception as e:
        logger.warning(f"Is class c error: {e}", exc_info=True)

    return False


def is_class_d(_, message: Message) -> bool:
    # Check if the message is Class D object
    try:
        if message.from_user:
            uid = message.from_user.id
            if uid in glovar.bad_ids["users"]:
                return True

        if message.forward_from:
            fid = message.forward_from.id
            if fid in glovar.bad_ids["users"]:
                return True

        if message.forward_from_chat:
            cid = message.forward_from_chat.id
            if cid in glovar.bad_ids["channels"]:
                return True
    except Exception as e:
        logger.warning(f"Is class d error: {e}", exc_info=True)

    return False


def is_class_e(_, message: Message) -> bool:
    # Check if the message is Class E object
    try:
        if message.forward_from_chat:
            cid = message.forward_from_chat.id
            if cid in glovar.except_ids["channels"]:
                return True
    except Exception as e:
        logger.warning(f"Is class e error: {e}", exc_info=True)

    return False


def is_declared_message(_, message: Message) -> bool:
    # Check if the message is declared by other bots
    try:
        if message.chat:
            gid = message.chat.id
            mid = message.message_id
            return is_declared_message_id(gid, mid)
    except Exception as e:
        logger.warning(f"Is declared message error: {e}", exc_info=True)

    return False


def is_exchange_channel(_, message: Message) -> bool:
    # Check if the message is sent from the exchange channel
    try:
        if message.chat:
            cid = message.chat.id
            if glovar.should_hide:
                if cid == glovar.hide_channel_id:
                    return True
            elif cid == glovar.exchange_channel_id:
                return True
    except Exception as e:
        logger.warning(f"Is exchange channel error: {e}", exc_info=True)

    return False


def is_hide_channel(_, message: Message) -> bool:
    # Check if the message is sent from the hide channel
    try:
        if message.chat:
            cid = message.chat.id
            if cid == glovar.hide_channel_id:
                return True
    except Exception as e:
        logger.warning(f"Is hide channel error: {e}", exc_info=True)

    return False


def is_new_group(_, message: Message) -> bool:
    # Check if the bot joined a new group
    try:
        if message.new_chat_members:
            new_users = message.new_chat_members
            if new_users:
                for user in new_users:
                    if user.is_self:
                        return True
        elif message.group_chat_created or message.supergroup_chat_created:
            return True
    except Exception as e:
        logger.warning(f"Is new group error: {e}", exc_info=True)

    return False


def is_test_group(_, message: Message) -> bool:
    # Check if the message is sent from the test group
    try:
        if message.chat:
            cid = message.chat.id
            if cid == glovar.test_group_id:
                return True
    except Exception as e:
        logger.warning(f"Is test group error: {e}", exc_info=True)

    return False


class_c = Filters.create(
    func=is_class_c,
    name="Class C"
)

class_d = Filters.create(
    func=is_class_d,
    name="Class D"
)

class_e = Filters.create(
    func=is_class_e,
    name="Class E"
)

declared_message = Filters.create(
    func=is_declared_message,
    name="Declared message"
)

exchange_channel = Filters.create(
    func=is_exchange_channel,
    name="Exchange Channel"
)

hide_channel = Filters.create(
    func=is_hide_channel,
    name="Hide Channel"
)

new_group = Filters.create(
    func=is_new_group,
    name="New Group"
)

test_group = Filters.create(
    func=is_test_group,
    name="Test Group"
)


def is_declared_message_id(gid: int, mid: int) -> bool:
    # Check if the message's ID is declared by other bots
    try:
        if mid in glovar.declared_message_ids.get(gid, set()):
            return True
    except Exception as e:
        logger.warning(f"Is declared message id error: {e}", exc_info=True)

    return False


def is_detected_url(message: Message) -> str:
    # Check if the message include detected url, return detected types as set
    try:
        gid = message.chat.id
        links = get_links(message)
        for link in links:
            detected_type = glovar.contents.get(link, "")
            if detected_type and is_in_config(gid, detected_type):
                return detected_type
    except Exception as e:
        logger.warning(f"Is detected url error: {e}", exc_info=True)

    return ""


def is_detected_user(message: Message) -> bool:
    # Check if the message is sent by a detected user
    try:
        if message.from_user:
            gid = message.chat.id
            uid = message.from_user.id
            return is_detected_user_id(gid, uid)
    except Exception as e:
        logger.warning(f"Is detected user error: {e}", exc_info=True)

    return False


def is_detected_user_id(gid: int, uid: int) -> bool:
    # Check if the user_id is detected in the group
    try:
        user = glovar.user_ids.get(uid, {})
        if user:
            status = user["detected"].get(gid, 0)
            now = get_now()
            if now - status < glovar.punish_time:
                return True
    except Exception as e:
        logger.warning(f"Is detected user id error: {e}", exc_info=True)

    return False


def is_high_score_user(message: Message) -> Union[bool, float]:
    # Check if the message is sent by a high score user
    try:
        if message.from_user:
            uid = message.from_user.id
            user = glovar.user_ids.get(uid, {})
            if user:
                score = 0.0
                try:
                    user = glovar.user_ids.get(uid, {})
                    if user:
                        score = (user["score"].get("captcha", 0.0)
                                 + user["score"].get("clean", 0.0)
                                 + user["score"].get("lang", 0.0)
                                 + user["score"].get("long", 0.0)
                                 + user["score"].get("noflood", 0.0)
                                 + user["score"].get("noporn", 0.0)
                                 + user["score"].get("nospam", 0.0)
                                 + user["score"].get("recheck", 0.0)
                                 + user["score"].get("warn", 0.0))
                except Exception as e:
                    logger.warning(f"Get score error: {e}", exc_info=True)

                if score >= 3.0:
                    return score
    except Exception as e:
        logger.warning(f"Is high score user error: {e}", exc_info=True)

    return False


def is_in_config(gid: int, the_type: str) -> bool:
    # Check if the type is in the group's config
    try:
        if glovar.configs.get(gid, {}):
            return glovar.configs[gid].get(the_type, False)
    except Exception as e:
        logger.warning(f"Is in config error: {e}", exc_info=True)

    return False


def is_not_allowed(client: Client, message: Message, text: str = None, image_path: str = None) -> str:
    # Check if the message is not allowed in the group
    result = ""
    if image_path:
        need_delete = [image_path]
    else:
        need_delete = []

    if glovar.locks["message"].acquire():
        try:
            gid = message.chat.id

            # Regular message
            if not (text or image_path):
                # If the user is being punished
                if is_detected_user(message):
                    return "true"

                # If the message has been detected
                content = get_content(client, message)
                if content:
                    detection = glovar.contents.get(content, "")
                    if detection and is_in_config(gid, detection):
                        return detection

                # Privacy messages

                # Contact
                if is_in_config(gid, "con"):
                    if message.contact:
                        return "con"

                # Location
                if is_in_config(gid, "loc"):
                    if message.location or message.venue:
                        return "loc"

                # Video note
                if is_in_config(gid, "vdn"):
                    if message.video_note:
                        return "vdn"

                # Voice
                if is_in_config(gid, "voi"):
                    if message.voice:
                        return "voi"

                # Basic types messages

                # Animated Sticker
                # if is_in_config(gid, "ast"):
                #     if message.sticker and message.sticker.is_animated:
                #         return "ast"

                # Audio
                if is_in_config(gid, "aud"):
                    if message.audio:
                        return "aud"

                # Bot command
                if is_in_config(gid, "bmd"):
                    text = get_text(message)
                    if re.search("^/", text):
                        if not get_command_type(message):
                            return "bmd"

                # Document
                if is_in_config(gid, "doc"):
                    if message.document:
                        return "doc"

                # Game
                if is_in_config(gid, "gam"):
                    if message.game:
                        return "gam"

                # GIF
                if is_in_config(gid, "gif"):
                    if (message.animation
                            or (message.document
                                and message.document.mime_type
                                and "gif" in message.document.mime_type)):
                        return "gif"

                # Via Bot
                if is_in_config(gid, "via"):
                    if message.via_bot:
                        return "via"

                # Video
                if is_in_config(gid, "vid"):
                    if message.video:
                        return "vid"

                # Service
                if is_in_config(gid, "ser"):
                    if message.service:
                        return "ser"

                # Sticker
                if is_in_config(gid, "sti"):
                    return "sti"

                # Spam messages

                text = get_text(message)

                # AFF link
                if is_in_config(gid, "aff"):
                    if is_regex_text("aff", text):
                        return "aff"

                # Executive file
                if is_in_config(gid, "exe"):
                    if message.document:
                        if message.document.file_name:
                            file_name = message.document.file_name
                            for file_type in ["apk", "bat", "cmd", "com", "exe", "vbs"]:
                                if re.search(f"{file_type}$", file_name, re.I):
                                    return "exe"

                        if message.document.mime_type:
                            mime_type = message.document.mime_type
                            if "executable" in mime_type:
                                return "exe"

                # Instant messenger link
                if is_in_config(gid, "iml"):
                    if is_regex_text("iml", text):
                        return "iml"

                # Short link
                if is_in_config(gid, "sho"):
                    if is_regex_text("sho", text):
                        return "sho"

                # Telegram link
                if is_in_config(gid, "tgl"):
                    bypass = get_stripped_link(get_channel_link(message))
                    links = get_links(message)
                    tg_links = filter(lambda l: is_regex_text("tgl", l), links)
                    if not all([bypass in link for link in tg_links]):
                        return "tgl"

                    if message.entities:
                        for en in message.entities:
                            if en.type == "mention":
                                username = get_entity_text(message, en)[1:]
                                peer_type, _ = resolve_username(client, username)
                                if peer_type == "channel":
                                    return "tgl"

                # Telegram proxy
                if is_in_config(gid, "tgp"):
                    if is_regex_text("tgp", text):
                        return "tgp"

                # QR code
                if is_in_config(gid, "qrc"):
                    file_id = get_file_id(message)
                    image_path = get_downloaded_path(client, file_id)
                    if is_declared_message(None, message):
                        return ""
                    elif image_path:
                        need_delete.append(image_path)
                        qrcode = get_qrcode(image_path)
                        if qrcode:
                            return "qrc"

                # Schedule to delete stickers and animations
                if is_in_config(gid, "ttd"):
                    if (message.sticker
                            or message.animation
                            or (message.document
                                and message.document.mime_type
                                and "gif" in message.document.mime_type)):
                        mid = message.message_id
                        glovar.message_ids[gid]["stickers"].append(mid)
                        save("message_ids")
                        return ""

            # Preview message
            else:
                if text:
                    # AFF link
                    if is_in_config(gid, "aff"):
                        if is_regex_text("aff", text):
                            return "aff"

                    # Instant messenger link
                    if is_in_config(gid, "iml"):
                        if is_regex_text("iml", text):
                            return "iml"

                    # Short link
                    if is_in_config(gid, "sho"):
                        if is_regex_text("sho", text):
                            return "sho"

                    # Telegram link
                    if is_in_config(gid, "tgl"):
                        if is_regex_text("tgl", text):
                            return "tgl"

                    # Telegram proxy
                    if is_in_config(gid, "tgp"):
                        if is_regex_text("tgp", text):
                            return "tgp"

                # QR code
                if image_path:
                    qrcode = get_qrcode(image_path)
                    if qrcode:
                        return "qrc"
        except Exception as e:
            logger.warning(f"Is not allowed error: {e}", exc_info=True)
        finally:
            glovar.locks["message"].release()

            for file in need_delete:
                delete_file(file)

    return result


def is_regex_text(word_type: str, text: str) -> bool:
    # Check if the text hit the regex rules
    result = False
    try:
        if text:
            text = text.replace("\n", " ")
            text = re.sub(r"\s\s", " ", text)
            text = re.sub(r"\s\s", " ", text)
        else:
            return False

        for word in list(eval(f"glovar.{word_type}_words")):
            if re.search(word, text, re.I | re.S | re.M):
                result = True
            else:
                text = re.sub(r"\s", "", text)
                if re.search(word, text, re.I | re.S | re.M):
                    result = True

            if result:
                count = eval(f"glovar.{word_type}_words").get(word, 0)
                count += 1
                eval(f"glovar.{word_type}_words")[word] = count
                save(f"{word_type}_words")
                return result
    except Exception as e:
        logger.warning(f"Is regex text error: {e}", exc_info=True)

    return False


def is_watch_user(message: Message, the_type: str) -> bool:
    # Check if the message is sent by a watch user
    try:
        if message.from_user:
            uid = message.from_user.id
            now = get_now()
            until = glovar.watch_ids[the_type].get(uid, 0)
            if now < until:
                return True
    except Exception as e:
        logger.warning(f"Is watch user error: {e}", exc_info=True)

    return False
