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
import pickle
from configparser import RawConfigParser
from os import mkdir
from os.path import exists
from shutil import rmtree
from threading import Lock
from typing import Dict, List, Set, Union

from pyrogram import Chat

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING,
    filename='log',
    filemode='w'
)
logger = logging.getLogger(__name__)

# Read data from config.ini

# [basic]
bot_token: str = ""
prefix: List[str] = []
prefix_str: str = "/!"

# [bots]
avatar_id: int = 0
captcha_id: int = 0
clean_id: int = 0
lang_id: int = 0
long_id: int = 0
noflood_id: int = 0
noporn_id: int = 0
nospam_id: int = 0
recheck_id: int = 0
tip_id: int = 0
user_id: int = 0
warn_id: int = 0

# [channels]
critical_channel_id: int = 0
debug_channel_id: int = 0
exchange_channel_id: int = 0
hide_channel_id: int = 0
logging_channel_id: int = 0
test_group_id: int = 0

# [custom]
default_group_link: str = ""
image_size: int = 0
project_link: str = ""
project_name: str = ""
time_punish: int = 0
reset_day: str = ""
time_ban: int = 0
time_sticker: int = 0
zh_cn: Union[str, bool] = ""

# [encrypt]
key: Union[str, bytes] = ""
password: str = ""

try:
    config = RawConfigParser()
    config.read("config.ini")
    # [basic]
    bot_token = config["basic"].get("bot_token", bot_token)
    prefix = list(config["basic"].get("prefix", prefix_str))
    # [bots]
    avatar_id = int(config["bots"].get("avatar_id", avatar_id))
    captcha_id = int(config["bots"].get("captcha_id", captcha_id))
    clean_id = int(config["bots"].get("clean_id", clean_id))
    lang_id = int(config["bots"].get("lang_id", lang_id))
    long_id = int(config["bots"].get("long_id", long_id))
    noflood_id = int(config["bots"].get("noflood_id", noflood_id))
    noporn_id = int(config["bots"].get("noporn_id", noporn_id))
    nospam_id = int(config["bots"].get("nospam_id", nospam_id))
    recheck_id = int(config["bots"].get("recheck_id", recheck_id))
    tip_id = int(config["bots"].get("tip_id", tip_id))
    user_id = int(config["bots"].get("user_id", user_id))
    warn_id = int(config["bots"].get("warn_id", warn_id))
    # [channels]
    critical_channel_id = int(config["channels"].get("critical_channel_id", critical_channel_id))
    debug_channel_id = int(config["channels"].get("debug_channel_id", debug_channel_id))
    exchange_channel_id = int(config["channels"].get("exchange_channel_id", exchange_channel_id))
    hide_channel_id = int(config["channels"].get("hide_channel_id", hide_channel_id))
    logging_channel_id = int(config["channels"].get("logging_channel_id", logging_channel_id))
    test_group_id = int(config["channels"].get("test_group_id", test_group_id))
    # [custom]
    default_group_link = config["custom"].get("default_group_link", default_group_link)
    image_size = int(config["custom"].get("image_size", image_size))
    project_link = config["custom"].get("project_link", project_link)
    project_name = config["custom"].get("project_name", project_name)
    reset_day = config["custom"].get("reset_day", reset_day)
    time_ban = int(config["custom"].get("time_ban", time_ban))
    time_punish = int(config["custom"].get("time_punish", time_punish))
    time_sticker = int(config["custom"].get("time_sticker", time_sticker))
    zh_cn = config["custom"].get("zh_cn", zh_cn)
    zh_cn = eval(zh_cn)
    # [encrypt]
    key = config["encrypt"].get("key", key)
    key = key.encode("utf-8")
    password = config["encrypt"].get("password", password)
except Exception as e:
    logger.warning(f"Read data from config.ini error: {e}", exc_info=True)

# Check
if (bot_token in {"", "[DATA EXPUNGED]"}
        or prefix == []
        or avatar_id == 0
        or captcha_id == 0
        or clean_id == 0
        or lang_id == 0
        or long_id == 0
        or noflood_id == 0
        or noporn_id == 0
        or nospam_id == 0
        or recheck_id == 0
        or tip_id == 0
        or user_id == 0
        or warn_id == 0
        or critical_channel_id == 0
        or debug_channel_id == 0
        or exchange_channel_id == 0
        or hide_channel_id == 0
        or logging_channel_id == 0
        or test_group_id == 0
        or default_group_link in {"", "[DATA EXPUNGED]"}
        or image_size == 0
        or project_link in {"", "[DATA EXPUNGED]"}
        or project_name in {"", "[DATA EXPUNGED]"}
        or reset_day in {"", "[DATA EXPUNGED]"}
        or time_ban == 0
        or time_punish == 0
        or time_sticker == 0
        or zh_cn not in {False, True}
        or key in {b"", b"[DATA EXPUNGED]"}
        or password in {"", "[DATA EXPUNGED]"}):
    logger.critical("No proper settings")
    raise SystemExit("No proper settings")

bot_ids: Set[int] = {avatar_id, captcha_id, clean_id, lang_id, long_id,
                     noflood_id, noporn_id, nospam_id, recheck_id, tip_id, user_id, warn_id}

# Languages
lang: Dict[str, str] = {
    # Basic
    "action": (zh_cn and "执行操作") or "Action",
    "admin": (zh_cn and "管理员") or "Admin",
    "admin_group": (zh_cn and "群管理") or "Group Admin",
    "admin_project": (zh_cn and "项目管理员") or "Project Admin",
    "colon": (zh_cn and "：") or ": ",
    "config": (zh_cn and "设置") or "Settings",
    "config_change": (zh_cn and "更改设置") or "Change Config",
    "config_create": (zh_cn and "创建设置会话") or "Create Config Session",
    "config_button": (zh_cn and "请点击下方按钮进行设置") or "Press the Button to Config",
    "config_go": (zh_cn and "前往设置") or "Go to Config",
    "config_locked": (zh_cn and "设置当前被锁定") or "Config is Locked",
    "config_show": (zh_cn and "查看设置") or "Show Config",
    "config_updated": (zh_cn and "已更新") or "Updated",
    "command_lack": (zh_cn and "命令参数缺失") or "Lack of Parameter",
    "command_para": (zh_cn and "命令参数有误") or "Incorrect Command Parameter",
    "command_type": (zh_cn and "命令类别有误") or "Incorrect Command Type",
    "command_usage": (zh_cn and "用法有误") or "Incorrect Usage",
    "custom": (zh_cn and "自定义") or "Custom",
    "custom_group": (zh_cn and "群组自定义") or "Group Custom",
    "default": (zh_cn and "默认") or "Default",
    "description": (zh_cn and "说明") or "Description",
    "disabled": (zh_cn and "禁用") or "Disabled",
    "enabled": (zh_cn and "启用") or "Enabled",
    "from_name": (zh_cn and "来源名称") or "Forward Name",
    "group_id": (zh_cn and "群组 ID") or "Group ID",
    "group_name": (zh_cn and "群组名称") or "Group Name",
    "inviter": (zh_cn and "邀请人") or "Inviter",
    "leave_approve": (zh_cn and "已批准退出群组") or "Approve to Leave the Group",
    "leave_auto": (zh_cn and "自动退出并清空数据") or "Leave automatically",
    "level": (zh_cn and "操作等级") or "Level",
    "project": (zh_cn and "项目编号") or "Project",
    "project_origin": (zh_cn and "原始项目") or "Original Project",
    "message_freq": (zh_cn and "消息频率") or "Message Frequency",
    "message_game": (zh_cn and "游戏标识") or "Game Short Name",
    "message_lang": (zh_cn and "消息语言") or "Message Language",
    "message_type": (zh_cn and "消息类别") or "Message Type",
    "more": (zh_cn and "附加信息") or "Extra Info",
    "name": (zh_cn and "名称") or "Name",
    "reason": (zh_cn and "原因") or "Reason",
    "reason_admin": (zh_cn and "获取管理员列表失败") or "Failed to Fetch Admin List",
    "reason_leave": (zh_cn and "非管理员或已不在群组中") or "Not Admin in Group",
    "reason_permissions": (zh_cn and "权限缺失") or "Missing Permissions",
    "reason_unauthorized": (zh_cn and "未授权使用") or "Unauthorized",
    "reason_user": (zh_cn and "缺失 USER") or "Missing USER",
    "refresh": (zh_cn and "刷新群管列表") or "Refresh Admin Lists",
    "rule": (zh_cn and "规则") or "Rule",
    "score": (zh_cn and "评分") or "Score",
    "status": (zh_cn and "状态") or "Status",
    "status_joined": (zh_cn and "已加入群组") or "Joined the Group",
    "status_left": (zh_cn and "已退出群组") or "Left the Group",
    "status_succeed": (zh_cn and "成功执行") or "Succeed",
    "triggered_by": (zh_cn and "触发消息") or "Triggered By",
    "user": (zh_cn and "用户") or "User",
    "user_bio": (zh_cn and "用户简介") or "User Bio",
    "user_id": (zh_cn and "用户 ID") or "User ID",
    "user_name": (zh_cn and "用户昵称") or "User Name",
    "user_score": (zh_cn and "用户得分") or "User Score",
    "version": (zh_cn and "版本") or "Version",
    # Emergency
    "auto_fix": (zh_cn and "自动处理") or "Auto Fix",
    "emergency_channel": (zh_cn and "应急频道") or "Emergency Channel",
    "exchange_invalid": (zh_cn and "数据交换频道失效") or "Exchange Channel Invalid",
    "issue": (zh_cn and "发现状况") or "Issue",
    "protocol_1": (zh_cn and "启动 1 号协议") or "Initiate Protocol 1",
    "transfer_channel": (zh_cn and "频道转移") or "Transfer Channel",
    # More
    "privacy": (zh_cn and "可能涉及隐私而未转发") or "Not Forwarded Due to Privacy Reason",
    "cannot_forward": (zh_cn and "此类消息无法转发至频道") or "The Message Cannot be Forwarded to Channel",
    # Message Types
    "gam": (zh_cn and "游戏") or "Game",
    "ser": (zh_cn and "服务消息") or "Service",
    # Special Types
    "con": (zh_cn and "联系人") or "Contact",
    "loc": (zh_cn and "定位地址") or "Location",
    "vdn": (zh_cn and "圆视频") or "Round Video",
    "voi": (zh_cn and "语音") or "Voice",
    "ast": (zh_cn and "动态贴纸") or "Animated Sticker",
    "aud": (zh_cn and "音频") or "Audio",
    "bmd": (zh_cn and "机器人命令") or "Bot Command",
    "doc": (zh_cn and "文件") or "Document",
    "gif": (zh_cn and "GIF 动图") or "GIF",
    "via": (zh_cn and "通过 Bot 发送的消息") or "Via Bot",
    "vid": (zh_cn and "视频") or "Video",
    "sti": (zh_cn and "贴纸") or "Sticker",
    "aff": (zh_cn and "推广链接") or "AFF Link",
    "exe": (zh_cn and "可执行文件") or "Executable File",
    "iml": (zh_cn and "即时通讯联系方式") or "IM Link",
    "sho": (zh_cn and "短链接") or "Short Link",
    "tgl": (zh_cn and "TG 链接") or "Telegram Link",
    "tgp": (zh_cn and "TG 代理") or "Telegram Proxy",
    "qrc": (zh_cn and "二维码") or "QR Code",
    "sde": (zh_cn and "自助删除消息") or "Self Delete Messages",
    "tcl": (zh_cn and "每日自动清理群成员") or "Clean Members Everyday",
    "ttd": (zh_cn and "定时删除贴纸动图") or "Schedule to Delete Stickers",
    "pur": (zh_cn and "命令清空消息") or "Purge",
    "cln": (zh_cn and "命令清理消息") or "Clean Messages on Demand",
    # Special
    "clean_action": (zh_cn and "清理消息") or "Clean Messages",
    "clean_blacklist": (zh_cn and "清理黑名单") or "Clean Blacklist",
    "clean_debug": (zh_cn and "清理消息") or "Clean Messages",
    "clean_members": (zh_cn and "清理用户") or "Clean Members",
    "clean_more": (zh_cn and "群管要求删除贴纸动图") or "Group Admin's Decision",
    "filter": (zh_cn and "过滤") or "Filter",
    "ignore": (zh_cn and "忽略") or "Ignore",
    "invalid_user": (zh_cn and "失效用户") or "Deleted Account",
    "pur_action": (zh_cn and "清除消息") or "Purge Messages",
    "pur_debug": (zh_cn and "指定删除") or "Purge on Demand",
    "pur_more": (zh_cn and "群管要求删除指定消息") or "Group Admin's Decision",
    "schedule_delete": (zh_cn and "定时删除") or "Schedule to Delete",
    "sde_action": (zh_cn and "自助删除") or "Self Deletion",
    "sde_more": (zh_cn and "用户要求删除其全部消息") or "",
    "sticker": (zh_cn and "匹配消息") or "Sticker",
    # Terminate
    "auto_ban": (zh_cn and "自动封禁") or "Auto Ban",
    "auto_delete": (zh_cn and "自动删除") or "Auto Delete",
    "name_ban": (zh_cn and "名称封禁") or "Ban by Name",
    "name_examine": (zh_cn and "名称检查") or "Name Examination",
    "score_ban": (zh_cn and "评分封禁") or "Ban by Score",
    "score_user": (zh_cn and "用户评分") or "High Score",
    "watch_ban": (zh_cn and "追踪封禁") or "Watch Ban",
    "watch_delete": (zh_cn and "追踪删除") or "Watch Delete",
    "watch_user": (zh_cn and "敏感追踪") or "Watched User",
    # Test
    "record_content": (zh_cn and "过滤记录") or "Recorded content",
    "record_link": (zh_cn and "过滤链接") or "Recorded link",
    "white_listed": (zh_cn and "白名单") or "White Listed",
    # Unit
    "members": (zh_cn and "名") or "member(s)",
    "messages": (zh_cn and "条") or "message(s)"
}

# Init

all_commands: List[str] = [
    "clean",
    "config",
    "config_clean",
    "dafm",
    "purge",
    "version",
    "mention"
]

chats: Dict[int, Chat] = {}
# chats = {
#     -10012345678: Chat
# }

cleaned_ids: Set[int] = set()
# cleaned_ids = {-10012345678}

contents: Dict[str, str] = {}
# contents = {
#     "content": "tgl"
# }

declared_message_ids: Dict[int, Set[int]] = {}
# declared_message_ids = {
#     -10012345678: {123}
# }

deleted_ids: Dict[int, Set[int]] = {}
# deleted_ids = {
#     -10012345678: {12345678}
# }

default_config: Dict[str, Union[bool, int]] = {
    "default": True,
    "lock": 0,
    "con": True,
    "loc": True,
    "vdn": True,
    "voi": True,
    "ast": False,
    "aud": False,
    "bmd": False,
    "doc": False,
    "gam": False,
    "gif": False,
    "via": False,
    "vid": False,
    "ser": True,
    "sti": False,
    "aff": False,
    "exe": False,
    "iml": False,
    "sho": False,
    "tgl": False,
    "tgp": False,
    "qrc": False,
    "sde": False,
    "tcl": False,
    "ttd": False
}

default_user_status: Dict[str, Dict[Union[int, str], Union[float, int]]] = {
    "detected": {},
    "score": {
        "captcha": 0.0,
        "clean": 0.0,
        "lang": 0.0,
        "long": 0.0,
        "noflood": 0.0,
        "noporn": 0.0,
        "nospam": 0.0,
        "recheck": 0.0,
        "warn": 0.0
    }
}

left_group_ids: Set[int] = set()

locks: Dict[str, Lock] = {
    "admin": Lock(),
    "message": Lock(),
    "regex": Lock(),
    "test": Lock()
}

names: Dict[str, str] = {
    "con": lang.get("con", "con"),
    "loc": lang.get("loc", "loc"),
    "vdn": lang.get("vdn", "vdn"),
    "voi": lang.get("voi", "voi"),
    "ast": lang.get("ast", "ast"),
    "aud": lang.get("aud", "aud"),
    "bmd": lang.get("bmd", "bmd"),
    "doc": lang.get("doc", "doc"),
    "gam": lang.get("gam", "gam"),
    "gif": lang.get("gif", "gif"),
    "via": lang.get("via", "via"),
    "vid": lang.get("vid", "vid"),
    "ser": lang.get("ser", "ser"),
    "sti": lang.get("sti", "sti"),
    "aff": lang.get("aff", "aff"),
    "exe": lang.get("exe", "ext"),
    "iml": lang.get("iml", "iml"),
    "sho": lang.get("sho", "sho"),
    "tgl": lang.get("tgl", "tgl"),
    "tgp": lang.get("tgp", "tgp"),
    "qrc": lang.get("qrc", "qrc"),
    "sde": lang.get("sde", "sde"),
    "tcl": lang.get("tcl", "tcl"),
    "ttd": lang.get("ttd", "ttd"),
    "pur": lang.get("pur", "pur"),
    "cln": lang.get("cln", "cln")
}

other_commands: Set[str] = {
    "admin",
    "admins",
    "ban",
    "config_captcha",
    "config_lang",
    "config_long",
    "config_noflood",
    "config_noporn",
    "config_nospam",
    "config_tip",
    "config_user",
    "config_warn",
    "content",
    "dafm",
    "forgive",
    "kick",
    "l",
    "long",
    "mention",
    "print",
    "purge",
    "report",
    "t2s",
    "unban",
    "undo",
    "version",
    "warn"
}

purged_ids: Set[int] = set()
# purged_ids = {-10012345678}

receivers: Dict[str, List[str]] = {
    "bad": ["ANALYZE", "APPLY", "APPEAL", "AVATAR", "CAPTCHA", "CLEAN", "LANG", "LONG",
            "MANAGE", "NOFLOOD", "NOPORN", "NOSPAM", "RECHECK", "TIP", "USER", "WATCH"],
    "declare": ["ANALYZE", "AVATAR", "CLEAN", "LANG", "LONG",
                "NOFLOOD", "NOPORN", "NOSPAM", "RECHECK", "USER", "WATCH"],
    "score": ["ANALYZE", "CAPTCHA", "CLEAN", "LANG", "LONG",
              "MANAGE", "NOFLOOD", "NOPORN", "NOSPAM", "RECHECK"],
    "watch": ["ANALYZE", "CAPTCHA", "CLEAN", "LANG", "LONG",
              "MANAGE", "NOFLOOD", "NOPORN", "NOSPAM", "RECHECK", "WATCH"]
}

recorded_ids: Dict[int, Set[int]] = {}
# recorded_ids = {
#     -10012345678: {12345678}
# }

regex: Dict[str, bool] = {
    "ad": False,
    "aff": True,
    "ban": False,
    "con": False,
    "del": False,
    "iml": True,
    "sho": True,
    "spc": False,
    "spe": False,
    "tgl": True,
    "tgp": True,
    "wb": True
}

sender: str = "CLEAN"

should_hide: bool = False

types: Dict[str, Union[List[str], Set[str]]] = {
    "all": ["con", "loc", "vdn", "voi", "ast", "aud", "bmd", "doc", "gam", "gif", "via", "vid", "ser", "sti", "aff",
            "exe", "iml", "sho", "tgl", "tgp", "qrc"],
    "function": ["sde", "tcl", "ttd"],
    "spam": {"aff", "exe", "iml", "qrc", "sho", "tgl", "tgp", "true"}
}

version: str = "0.0.8"

# Load data from pickle

# Init dir
try:
    rmtree("tmp")
except Exception as e:
    logger.info(f"Remove tmp error: {e}")

for path in ["data", "tmp"]:
    if not exists(path):
        mkdir(path)

# Init ids variables

admin_ids: Dict[int, Set[int]] = {}
# admin_ids = {
#     -10012345678: {12345678}
# }

bad_ids: Dict[str, Set[Union[int, str]]] = {
    "channels": set(),
    "users": set()
}
# bad_ids = {
#     "channels": {-10012345678},
#     "users": {12345678}
# }

except_ids: Dict[str, Set[Union[int, str]]] = {
    "channels": set(),
    "long": set(),
    "temp": set()
}
# except_ids = {
#     "channels": {-10012345678},
#     "long": {"content"},
#     "temp": {"content"}
# }

message_ids: Dict[int, Dict[str, Union[int, Dict[int, int]]]] = {}
# message_ids = {
#     -10012345678: {
#         "service": 123,
#         "stickers": {
#             456: 1512345678,
#             789: 1512346678
#         }
#     }
# }

user_ids: Dict[int, Dict[str, Dict[Union[int, str], Union[float, int]]]] = {}
# user_ids = {
#     12345678: {
#         "detected": {
#               -10012345678: 1512345678
#         },
#         "score": {
#             "captcha": 0.0,
#             "clean": 0.0,
#             "lang": 0.0,
#             "long": 0.0,
#             "noflood": 0.0,
#             "noporn": 0.0,
#             "nospam": 0.0,
#             "recheck": 0.0,
#             "warn": 0.0
#         }
#     }
# }

watch_ids: Dict[str, Dict[int, int]] = {
    "ban": {},
    "delete": {}
}
# watch_ids = {
#     "ban": {
#         12345678: 0
#     },
#     "delete": {
#         12345678: 0
#     }
# }

# Init data variables

configs: Dict[int, Dict[str, Union[bool, int]]] = {}
# configs = {
#     -10012345678: {
#         "default": True,
#         "lock": 0,
#         "con": True,
#         "loc": True,
#         "vdn": True,
#         "voi": True,
#         "ast": False,
#         "aud": False,
#         "bmd": False,
#         "doc": False,
#         "gam": False,
#         "gif": False,
#         "via": False,
#         "vid": False,
#         "ser": True,
#         "sti": False,
#         "aff": False,
#         "exe": False,
#         "iml": False,
#         "sho": False,
#         "tgl": False,
#         "tgp": False,
#         "qrc": False,
#         "sde": False,
#         "tcl": False,
#         "ttd": False
#     }
# }

# Init word variables

for word_type in regex:
    locals()[f"{word_type}_words"]: Dict[str, Dict[str, Union[float, int]]] = {}

# type_words = {
#     "regex": 0
# }

# Load data
file_list: List[str] = ["admin_ids", "bad_ids", "except_ids", "message_ids", "user_ids", "watch_ids", "configs"]
file_list += [f"{f}_words" for f in regex]
for file in file_list:
    try:
        try:
            if exists(f"data/{file}") or exists(f"data/.{file}"):
                with open(f"data/{file}", "rb") as f:
                    locals()[f"{file}"] = pickle.load(f)
            else:
                with open(f"data/{file}", "wb") as f:
                    pickle.dump(eval(f"{file}"), f)
        except Exception as e:
            logger.error(f"Load data {file} error: {e}", exc_info=True)
            with open(f"data/.{file}", "rb") as f:
                locals()[f"{file}"] = pickle.load(f)
    except Exception as e:
        logger.critical(f"Load data {file} backup error: {e}", exc_info=True)
        raise SystemExit("[DATA CORRUPTION]")

# Start program
copyright_text = (f"SCP-079-{sender} v{version}, Copyright (C) 2019 SCP-079 <https://scp-079.org>\n"
                  "Licensed under the terms of the GNU General Public License v3 or later (GPLv3+)\n")
print(copyright_text)
