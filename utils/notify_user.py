from asyncio import sleep

import discord
import re


from api.endpoints import API_ENDPOINTS
from api.request import send_request
from logger import errorLogger, infoLogger

deprecated_bot_token = []


async def notify_user(data, client):
    """
    notify mass users
    Args:
     - data, client
    """
    try:

        bot_token = data["payload"]["bot_token"]
        discord_id = data["payload"]["discord_id"]
        infoLogger.info(f" Processing token : {bot_token}")
        await client.close()
        await client.login(bot_token)
        infoLogger.info(f" Processing Discord ID : {discord_id}")
        user = await client.fetch_user(int(discord_id))
        await user.send(data["payload"]["message"])
        infoLogger.info(f" send message to : {user.name}")
        await client.close()
    except (Exception) as e:
        errorLogger.error(f" error on (74): {e}")


async def notify_group(data, guild):
    try:

        role_name = data["payload"]["group_name"]
        team_role = discord.utils.find(lambda r: r.name == role_name, guild.roles)
        if not team_role:
            errorLogger.error(f" No Role present {role_name}")
            return
        team_channel_name = re.sub(" +", " ", re.sub("[^a-zA-Z0-9 \n]", "_", role_name))
        team_channel = "-".join(str(x).lower() for x in team_channel_name.split(" "))

        team_text_channel = discord.utils.find(lambda r: r.name == team_channel + "-channel", guild.text_channels)

        if not team_text_channel:
            errorLogger.error(f" No Channel present {team_channel}")
            return
        await team_text_channel.send(f'{team_role.mention} {data["payload"]["message"]}')
        infoLogger.info(f' SENDING {data["payload"]["message"]} ->>>>>> {team_text_channel.name}')

        await sleep(1)
    except (Exception) as e:
        errorLogger.error(f' error on assign_role:{data["payload"]["discord_id"]} error:  {e}')
