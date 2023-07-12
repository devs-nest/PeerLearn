from asyncio import sleep

import discord

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

        bot_id = data["payload"]["bot_id"]
        # Fetching the data from the servers
        bot_token = await send_request(endpoint=f'{API_ENDPOINTS["NOTIFICATION_BOT"]}{bot_id})')
        infoLogger.info(f" Processing token : {bot_token}")
        await client.close()
        await client.login(bot_token)
        new_token = bot_token
        index = 0
        retry_count = 0
        while index < len(data["payload"]["discord_id"]):
            try:
                discord_id = data["payload"]["discord_id"][index]
                infoLogger.info(f" Processing Discord ID : {discord_id}")
                index += 1
                user = await client.fetch_user(int(discord_id))
                await user.send(data["payload"]["message"])
                infoLogger.info(f" send message to : {user.name}")
            except (Exception) as e:
                if e.status and e.code and e.status == 403 and e.code not in [50007, 50001]:
                    # Forbidden has many error code so we can not call it's class discord.error.Forbidden rather check by code
                    errorLogger.error(f"Error:{e}")
                    if retry_count < 2:
                        index -= 1
                    if new_token not in deprecated_bot_token:
                        deprecated_bot_token.append(new_token)

                    try:
                        while new_token in deprecated_bot_token:
                            if retry_count > 2:
                                index += 1
                                await client.close()
                                await sleep(1)
                                break
                            try:
                                retry_count += 1
                                infoLogger.info(f" RETRY COUNT ======== : {retry_count}")
                                new_token = await send_request(endpoint=f'{API_ENDPOINTS["NOTIFICATION_BOT"]}{bot_id}')
                                infoLogger.info(f" Waiting for token : {new_token} for BOT {bot_id}")
                                await sleep(5)
                                await send_request(
                                    endpoint=f'{API_ENDPOINTS["NOTIFICATION_BOT"]}{bot_id}/change_token'
                                )
                                # Sleeping for 5 sec to change the bot
                            except (Exception) as e:
                                errorLogger.error(f"Request Failed (63):{e}")

                        await client.close()
                        await client.login(new_token)

                    except (Exception) as e:
                        errorLogger.error(f"Request Failed 69):{e}")
                else:
                    errorLogger.error(f" Error on sending message to {data['payload']['discord_id']}-------> {e}")
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
        team_channel = "-".join(str(x).lower() for x in role_name.split(" "))

        team_text_channel = discord.utils.find(lambda r: r.name == team_channel + "-channel", guild.text_channels)

        if not team_text_channel:
            errorLogger.error(f" No Channel present {team_channel}")
            return
        await team_text_channel.send(f'{team_role.mention} {data["payload"]["message"]}')
        infoLogger.info(f' SENDING {data["payload"]["message"]} ->>>>>> {team_text_channel.name}')

        await sleep(1)
    except (Exception) as e:
        errorLogger.error(f' error on assign_role:{data["payload"]["discord_id"]} error:  {e}')
