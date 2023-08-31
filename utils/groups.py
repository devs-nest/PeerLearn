import re

import discord

from logger import errorLogger, infoLogger

from api.endpoints import API_ENDPOINTS
from api.request import send_request

# from utils.config import CONFIG


async def create_group(data, guild):
    try:
        team_name = "PL " + data["payload"]["group_name"]
        course_type = data["payload"]["course_type"]
        team_role = discord.utils.find(
            lambda r: r.name == team_name, guild.roles)
        if not team_role:
            team_role = await guild.create_role(name=team_name, mentionable=True)
            infoLogger.info("Team Role created")
        team_channel_name = re.sub(
            " +", " ", re.sub("[^a-zA-Z0-9 \n]", "_", team_name))
        team_channel = "-".join(str(x).lower()
                                for x in team_channel_name.split(" "))
        category = discord.utils.find(
            lambda r: r.name == f"{course_type} Groups" and len(
                r.channels) < 48, guild.categories
        )
        if not category:
            # Create category if not present
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            category = await guild.create_category(f"{course_type} Groups", overwrites=overwrites)
            print(f"Category '{category.name}' created for {team_name}")

        temp_text_channel = discord.utils.find(
            lambda r: r.name == team_channel + "-channel", guild.text_channels
        )

        if not temp_text_channel:
            temp_text_channel = await guild.create_text_channel(team_channel + "-channel", category=category)
            infoLogger.info(f'{team_channel + "-channel"} created')
        await temp_text_channel.set_permissions(guild.default_role, view_channel=False)
        await temp_text_channel.set_permissions(team_role, view_channel=True)

    except (Exception) as e:
        errorLogger.error(f" error on creating_group:  {e}")


async def delete_group(data, guild):
    try:
        team_name = "PL " + data["payload"]["group_name"]
        team_role = discord.utils.find(
            lambda r: r.name == team_name, guild.roles)
        if team_role:
            await team_role.delete()
            infoLogger.info("Team Role destroy")
            team_channel_name = re.sub(
                " +", " ", re.sub("[^a-zA-Z0-9 \n]", "_", team_name))
            team_channel = "-".join(str(x).lower()
                                    for x in team_channel_name.split(" "))
            if team_channel_name:
                await team_channel_name.delete()
                infoLogger.info(f'{team_channel}-channel destroyed')

    except (Exception) as e:
        errorLogger.error(f" error on deleting_group:  {e}")


async def update_group(data, guild):
    try:
        name = data["payload"]["group_name"].split("`!`!`")
        old_name = "PL " + name[0]
        new_name = "PL " + name[1]

        team_role = discord.utils.find(
            lambda r: r.name == old_name, guild.roles)
        if team_role:
            await team_role.edit(name=new_name)
            infoLogger.info(f"{old_name} Updated to -->>> {new_name}")
        old_team_channel = "-".join(
            str(x).lower() for x in re.sub(" +", " ", re.sub("[^a-zA-Z0-9 \n]", "_", old_name)).split(" ")
        )
        new_team_channel = "-".join(
            str(x).lower() for x in re.sub(" +", " ", re.sub("[^a-zA-Z0-9 \n]", "_", new_name)).split(" ")
        )
        temp_text_channel = discord.utils.find(
            lambda r: r.name == old_team_channel + "-channel", guild.channels)
        if temp_text_channel:
            await temp_text_channel.edit(name=new_team_channel + "-channel")
            infoLogger.info(
                f'{old_team_channel + "-channel"} Updated to -->>> {new_team_channel + "-channel"}')

    except (Exception) as e:
        errorLogger.error(f" error on updating_group:  {e}")


async def start_scrum(data, guild):
    try:
        infoLogger.info(f"Starting Scrum for :  {data}")
        team_name = "PL " + data["payload"]["group_name"]
        group_name = "SCRUM " + data["payload"]["group_name"]
        course_type = data["payload"]["course_type"]
        category = discord.utils.find(
            lambda r: r.name == f"{course_type} Groups" and len(
                r.channels) < 48, guild.categories
        )
        if not category:
            # Create category if not present
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            category = await guild.create_category(f"{course_type} Groups", overwrites=overwrites)
            infoLogger.info(
                f"Category '{category.name}' created for {group_name}")

        # Create a voice channel for this team's scrum
        voice_channel = discord.utils.find(
            lambda r: r.name == group_name, guild.voice_channels
        )
        if not voice_channel:
            voice_channel = await guild.create_voice_channel(group_name, category=category)

        # Tag this voice channel in the group's text channel for the scrum
        team_role = discord.utils.find(
            lambda r: r.name == team_name, guild.roles)
        if not team_role:
            team_role = await guild.create_role(name=team_name, mentionable=True)
            infoLogger.info("Team Role created")
        team_channel_name = re.sub(
            " +", " ", re.sub("[^a-zA-Z0-9 \n]", "_", team_name))
        team_channel = "-".join(str(x).lower()
                                for x in team_channel_name.split(" "))
        temp_text_channel = discord.utils.find(
            lambda r: r.name == team_channel + "-channel", guild.text_channels
        )
        if temp_text_channel:
            # Mention the voice channel in the text channel
            mention = voice_channel.mention
            role_mention = team_role.mention

            await temp_text_channel.send(f"{role_mention} Scrum is starting! Join {mention} for the scrum.")
        else:
            # Handle the case when the text channel doesn't exist
            errorLogger.error("Text channel not found for the scrum group.")

        # Assuming you want to send a payload to an API endpoint
        payload = {
            "data": {
                "attributes": {
                    "server_guild": guild.id,
                    "channel_id": voice_channel.id,
                    "group_name": data["payload"]["group_name"]
                },
                "type": "groups"
            }
        }

        infoLogger.info(payload)
        resp = await send_request(method="POST", endpoint=API_ENDPOINTS["UPDATE_SCRUM_CHANNEL"], data=payload)

        infoLogger.info(resp)
    except (Exception) as e:
        errorLogger.error(f" error on starting scrum:  {e}")


async def check_channel_category(data, guild):
    try:
        channel_name = data['payload']['channel_name']
        btc_type = data['payload']['course_type']

        category_name = f"{btc_type} Groups"

        channel = discord.utils.get(guild.channels, name=channel_name)
        if channel and category_name != channel.category.name:
            # Move channel to correct category\
            category = discord.utils.find(
                lambda r: r.name == f"{btc_type} Groups" and len(
                    r.channels) < 48, guild.categories
            )
            if not category:
                # Create category if not present
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                }
                category = await guild.create_category(f"{btc_type} Groups", overwrites=overwrites)
            await channel.edit(category=category)
            infoLogger.info(
                f"Channel '{channel.name}' moved to category '{category.name}'")

    except (Exception) as e:
        errorLogger.error(f" error on checking channel category:  {e}")
