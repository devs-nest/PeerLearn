import datetime
import os
import re
import sys

import discord
import sentry_sdk

from client import client
from logger import errorLogger, infoLogger
from utils.config import CONFIG
from utils.embeds import Embeds
from utils.sqs import shoot_sqs
from api.request import send_request
from api.endpoints import API_ENDPOINTS

sentry_sdk.init(CONFIG["SENTRY_URL"], traces_sample_rate=0.9)


# if CONFIG["KEEP_ALIVE"]:
#     print("Starting keep alive thread")
#     keep_alive()


@client.event
async def on_guild_join(guild):
    infoLogger.info(f"Joined the server: {guild.name}")
    # TODO : Take Server name from backend
    # if str(guild.id) not in ["781576398414413854", "985833665940578304", "988415912820502589", "846802059210391603"]:
    #     await guild.leave()
    #     infoLogger.info(f"Left the server: {guild.name}")


@client.event
async def on_ready():
    infoLogger.info(f"Logged in as {client.user.name} {client.user.id}")
    infoLogger.info("-----------------------")
    game = discord.Game("with code")
    await client.change_presence(status=discord.Status.online, activity=game)
    # TODO : Take Server name from backend


# @client.event
# async def on_member_update(memberBefore, memberAfter):
#     # TODO : Reset Roles from Backend

@client.event
async def on_guild_join(guild):
    try:
        payload = {
            "data": {
                "attributes": {"server_guild": guild.id},
                "type": "servers"
            }
        }
        resp = await send_request(method="POST", endpoint=API_ENDPOINTS["CONNECT_SERVER"], data=payload)

        infoLogger.info(f"Server status successfully updated: {resp}")
    except Exception as e:
        errorLogger.error(f"Error while updating Server status ERROR: {e}")
# @ client.event
# async def on_message(message):
#     # TODO: Get user_details when user .info @user
#     # TODO: Get group_details when group .info @group
#     # TODO: Get Scrum_details when .scrum_info @group


# @ client.event
# async def on_member_join(member):
#     infoLogger.info(
#         f"{member.display_name} has joined {member.guild.name} id({member.id})")
#     try:


#         infoLogger.info(f"{member.name} added to DB ")
#         # Give user Roles
#         await give_user_roles(member)
#     except Exception as e:
#         errorLogger.error(f"Error while updating user status ERROR: {e}")


@ client.event
async def on_voice_state_update(member, before, after):
    try:
        if before.channel != after.channel and (after.channel and after.channel.name.startswith("SCRUM") or (
                before.channel and before.channel.name.startswith("SCRUM"))):

            if after.channel and after.channel.name.startswith("SCRUM"):
                group_name = after.channel.name
                entry_status = "in"
                scrum_channel = after.channel
            # User left a voice channel
            if before.channel and before.channel.name.startswith("SCRUM"):
                group_name = before.channel.name
                entry_status = "out"
                scrum_channel = before.channel

            payload = {
                "data": {
                    "attributes": {
                        "discord_id": member.id,
                        "server_guild": scrum_channel.guild.id,
                        "scrum_channel": scrum_channel.id,
                        "group_name": group_name.replace("SCRUM ", ""),
                        "entry_status": entry_status
                    },
                    "type": "groups"
                }
            }
            infoLogger.info(payload)
            resp = await send_request(method="POST", endpoint=API_ENDPOINTS["UPDATE_ATTENDANCE"], data=payload)
            infoLogger.info(resp)

    except Exception as e:
        errorLogger.error(f"Error while updating user attendance ERROR: {e}")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

args = sys.argv[1:]

for i in args:
    if i in ("--sqs"):
        shoot_sqs(client)

client.run(CONFIG["BOT_TOKEN"])
