import os
import re
import sys

import discord
import sentry_sdk

from client import client
from logger import errorLogger, infoLogger
from services.user import (
    assign_server,
    check_group_details,
    check_user_details,
    give_user_roles,
    new_member_joined,
    check_scrum_details,
)
from utils.config import CONFIG
from utils.embeds import Embeds
from utils.sqs import shoot_sqs

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
async def on_member_remove(member):
    try:
        infoLogger.info(
            f"User has left the server with user_id : {member.id} and username : {member.display_name}")
        await assign_server(member, False)
        infoLogger.info("User status successfully updated")
    except Exception as e:
        errorLogger.error(f"Error while updating user status ERROR: {e}")


@client.event
async def on_message(message):

    # TODO: Get user_details when user .info @user
    # TODO: Get group_details when group .info @group
    # TODO: Get Scrum_details when .scrum_info @group
    if message.content.startswith("dn-"):
        await client.process_commands(message)
    elif message.content.startswith(".info") and message.role_mentions:
        try:
            role_name = message.role_mentions[0].name
            channel = "-".join(
                str(x).lower() for x in re.sub(" +", " ", re.sub("[^a-zA-Z0-9 \n]", "_", role_name)).split(" ")
            )
            if (
                    message.channel.name == channel + "-channel"
                    and role_name.endswith("Team")
                    and role_name.startswith("V2")
            ):
                await check_group_details(message, role_name)
            elif message.channel.name == "bot-commands" and discord.utils.find(
                    lambda r: r.name == role_name, message.guild.roles
            ):
                member_list = []
                for member in message.guild.members:
                    if not member.bot and discord.utils.find(lambda r: r.name == role_name, member.roles):
                        member_list.append(
                            f"{member.id} ->>>> {member.display_name}")
                return Embeds.success_embed(
                    channel=message.channel,
                    title=f"{role_name} Details",
                    description="\n".join(_ for _ in member_list),
                )
        except Exception as e:
            errorLogger.error(f"Error on fetching role details: {e}")
            # return Embeds.error_embed(title="An error occurred while processing the command", channel=message.author)
    elif message.content.startswith(".info") and (
            message.channel.name == "ask-a-bot"
            or message.channel.name == "🐛bug-reports-and-ideas"
            or message.channel.name.startswith("v2")
    ):
        if message.mentions and (
                discord.utils.find(lambda r: r.name == "admin",
                                   message.author.roles)
                or discord.utils.find(lambda r: r.name == "Dn Beta Tester", message.author.roles)
        ):
            await check_user_details(message, message.mentions[0].id)
        elif message.mentions:
            return Embeds.error_embed(title="You can't get others data", channel=message.channel)
        else:
            await check_user_details(message, message.author.id, True)
    elif message.content.startswith(".scrums") and message.channel.name.startswith("v2") and message.role_mentions and (
            discord.utils.find(lambda r: r.name == "admin", message.author.roles)
            or discord.utils.find(lambda r: r.name == "Batch Leader", message.author.roles)
    ):
        role_name = message.role_mentions[0].name
        await check_scrum_details(message.channel, role_name)


@client.event
async def on_member_join(member):
    infoLogger.info(
        f"{member.display_name} has joined {member.guild.name} id({member.id})")
    try:
        # Register user in to DB
        await new_member_joined(member)
        # Assign server
        await assign_server(member)
        infoLogger.info(f"{member.name} added to DB ")
        # Give user Roles
        await give_user_roles(member)
    except Exception as e:
        errorLogger.error(f"Error while updating user status ERROR: {e}")


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run(CONFIG["BOT_TOKEN"])
