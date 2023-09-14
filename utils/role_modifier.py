import discord

from logger import errorLogger, infoLogger
from utils.config import CONFIG


async def assign_role(data, guild):
    try:
        role_name = "PL " + data["payload"]["role_name"]
        member = await guild.fetch_member(data["payload"]["discord_id"])
        role = discord.utils.find(lambda r: r.name == role_name, guild.roles)
        if role:
            if discord.utils.find(lambda r: r.name == role_name, member.roles):
                infoLogger.info(
                    f" {member.name} already has the role ->>>  {data['payload']['role_name']}")
            else:
                await member.add_roles(role)
                infoLogger.info(
                    f" Added role {data['payload']['role_name']} to -> {member.name}")
        else:
            errorLogger.error(
                f" No Role present {data['payload']['role_name']}")

    except (Exception) as e:
        errorLogger.error(
            f' error on assign_role:{data["payload"]["discord_id"]} error:  {e}')


async def take_role(data, guild):
    try:
        role_name = "PL " + data["payload"]["role_name"]
        member = await guild.fetch_member(data["payload"]["discord_id"])
        role = discord.utils.find(lambda r: r.name == role_name, guild.roles)
        if role:
            await member.remove_roles(role)
            infoLogger.info(f" Taken role {role_name} from -> {member.name}")

        else:
            errorLogger.error(f" No Role present {role_name}")
    except (Exception) as e:
        errorLogger.error(
            f' error on take_role:{data["payload"]["discord_id"]} error:  {e}')


async def assign_mass_role(data, guild):
    try:
        role = discord.utils.find(
            lambda r: r.name == data["payload"]["role_name"], guild.roles)
        if role:
            for discord_id in data["payload"]["discord_ids"]:
                try:
                    member = await guild.fetch_member(discord_id)
                    if discord.utils.find(lambda r: r.name == data["payload"]["role_name"], member.roles):
                        infoLogger.info(
                            f" {member.name} already has the role ->>>  {data['payload']['role_name']}")
                    else:
                        await member.add_roles(role)
                        infoLogger.info(
                            f" Added role {data['payload']['role_name']} to -> {member.name}")

                except (Exception) as e:
                    errorLogger.error(
                        f" error on assign_role:{discord_id} error:  {e}")
        else:
            errorLogger.error(
                f" No Role present {data['payload']['role_name']}")
    except (Exception) as e:
        errorLogger.error(f" error:  {e}")


async def take_mass_role(data, guild):
    try:
        role = discord.utils.find(
            lambda r: r.name == data["payload"]["role_name"], guild.roles)
        if role:
            for discord_id in data["payload"]["discord_ids"]:
                try:
                    member = await guild.fetch_member(discord_id)
                    await member.remove_roles(role)
                    infoLogger.info(
                        f" Taken role {data['payload']['role_name']} from -> {member.name}")
                except (Exception) as e:
                    errorLogger.error(
                        f" error on assign_role:{discord_id} error:  {e}")
        else:
            errorLogger.error(
                f" No Role present {data['payload']['role_name']}")

    except (Exception) as e:
        errorLogger.error(f" error:  {e}")
