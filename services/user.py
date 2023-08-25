import asyncio
import random
import re
from asyncio import sleep

import discord
import requests
from discord import Embed

from api.endpoints import API_ENDPOINTS
from api.request import send_request
from logger import errorLogger, infoLogger
from utils.channel import wrong_channel_prompt
from utils.config import CONFIG
from utils.embeds import Embeds
from utils.exception import BadRequest


async def check_channel_ask_a_bot(message):
    ch = message.channel
    if ch.name == "admin-lane":
        return True
    if ch.id != int(CONFIG["ASK_A_BOT"]) and type(ch).__name__ != "DMChannel":
        prompt = wrong_channel_prompt(
            "Type this command in 'Ask-a-Bot channel' or " "DM the bot to get the desired result !! "
        )
        asyncio.ensure_future(ch.send(embed=prompt))
        return False
    return True
