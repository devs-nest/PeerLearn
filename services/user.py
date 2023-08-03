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


# Send greeting msg to new user and post user details in DB
async def new_member_joined(member):
    resp = await submit_user_details(member)
    return resp


# Post user details in database
async def submit_user_details(member):
    name = re.sub("[^\\-a-zA-Z0-9 @#$&._-]", "_", member.name)
    display_name = re.sub("[^\\-a-zA-Z0-9. @#$&_-]", "_", member.display_name)
    password = get_password()

    payload = {
        "data": {
            "attributes": {
                "email": f"{member.name}_{str(member.id)[:4]}@discord.com",
                "name": display_name,
                "discord_username": display_name,
                "discord_id": str(member.id),
                "username": f"{name}{random.randint(1000, 9999)}",
                "password": password,
                "discord_active": 1,
            },
            "type": "users",
        }
    }
    try:
        resp = await send_request(method="POST", endpoint=API_ENDPOINTS["USERS"], data=payload)
        infoLogger.info("User request successfully sent")
    except (requests.exceptions.ConnectionError, BadRequest) as e:
        errorLogger.error("Error while registering the user to the database", e, payload)
        return

    return resp


def get_password():
    pwd = ""
    for i in range(10):
        pwd = pwd + str(random.randrange(10))
    return pwd


async def assign_server(member, active=True):
    payload = {
        "data": {
            "attributes": {"user_id": member.id, "server_id": member.guild.id, "active": active},
            "type": "server_users",
        }
    }
    try:
        await send_request(method="POST", endpoint=API_ENDPOINTS["ASSIGN_SERVER"], data=payload)
        infoLogger.info(f"Assigning {member.name} to {member.guild.name}")
    except (Exception) as e:
        errorLogger.error(f"Error while assigning server: {e}")


async def give_user_roles(member):
    dn_june_batch_role = discord.utils.find(lambda r: r.name == "DN JUNE BATCH", member.guild.roles)
    verified_role = discord.utils.find(lambda r: r.name == "Verified", member.guild.roles)
    payload = {
        "data": {
            "attributes": {
                "discord_id": member.id,
            },
            "type": "users",
        }
    }
    try:
        resp = await send_request(endpoint=API_ENDPOINTS["CHECK_GROUP_NAME"], data=payload)
        infoLogger.info(f"data : {resp}")
        group_name = resp["data"]["attributes"]["name"]
        if resp["data"]["attributes"]["server_guild_id"] != str(member.guild.id):
            infoLogger.info(f"{group_name} is not a part of {member.guild.name}")
        else:
            if group_name and dn_june_batch_role:
                await member.add_roles(dn_june_batch_role)
                infoLogger.info(f"DN JUNE BATCH role ->>> {member.display_name}")
                await member.add_roles(verified_role)
                infoLogger.info(f"Verified People role ->>> {member.display_name}")
            role = discord.utils.find(lambda r: r.name == group_name, member.guild.roles)
            # if not role:
            #     await create_group(data={"payload": {"group_name": [group_name]}}, guild=member.guild)
            # role = discord.utils.find(lambda r: r.name == group_name, member.guild.roles)
            if role:
                await member.add_roles(role)
                infoLogger.info(f"{group_name} role ->>> {member.display_name}")
            else:
                errorLogger.error(f"{group_name} role not found")
    except Exception as e:
        errorLogger.error(f"Error while fetching group name: {e}")


async def check_scrum_details(channel, role_name):
    payload = {
        "data": {
            "attributes": {
                "group_name": role_name,
                "server_id": channel.guild.id
            },
            "type": "groups",
        }
    }
    try:
        resp = await send_request(endpoint=API_ENDPOINTS["GROUPS_DATA"], data=payload)
        infoLogger.info(f"data : {resp}")
        embed = Embed(color=0x10B981, title=":white_check_mark: Scrum Details", channel=channel)
        for data in resp["data"]["attributes"]["result"]:
            print(data)
            description = ""
            user_name = data["user_name"]
            total_group_scrums = data["total_group_scrums"]
            # user_scrums_count = data["user_scrums_count"]
            scrum_attended_count = data["scrum_attended_count"]
            scrum_absent = data["scrum_absent"]
            class_rating_count = data["class_rating_count"]
            tha_progress_count = data["tha_progress_count"]
            topics_to_cover_count = data["topics_to_cover_count"]
            solved_assignments_count = data["solved_assignments_count"]
            recent_solved_assignments_count = data["recent_solved_assignments_count"]

            # if user_name:
            #     description += f"Name: {user_name} \n"
            if total_group_scrums:
                description += f"Total Group Scrums: {total_group_scrums} \n"
            if scrum_attended_count:
                description += f"Scrums Attended: {scrum_attended_count}\n"
            if scrum_absent:
                description += f"Scrums Missed: {scrum_absent})\n"
            if class_rating_count:
                description += f"Class Rating Filled: {class_rating_count}\n"
            if tha_progress_count:
                description += f"THA Progress Filled: {tha_progress_count}\n"
            if topics_to_cover_count:
                description += f"Topics Covered Filled: {topics_to_cover_count}\n"
            if solved_assignments_count:
                description += f"Solved Assignment: {solved_assignments_count}\n"
            if recent_solved_assignments_count:
                description += f"Recent Solved Assignment: {recent_solved_assignments_count}\n"
            description += "----------------------------------------------------------------\n"
            embed.add_field(name=f"{user_name} Details", value=description, inline=False)

        if description:
            return asyncio.ensure_future(channel.send(embed=embed))
    except Exception as e:
        errorLogger.error(f"Error on fetching group details: {e}")


async def check_group_details(message, role_name):
    member_list = {}
    for member in message.guild.members:
        if not member.bot and discord.utils.find(lambda r: r.name == role_name, member.roles):
            member_list[str(member.id)] = member.name
    payload = {
        "data": {
            "attributes": {
                "group_name": role_name,
                "server_id": message.guild.id
            },
            "type": "groups",
        }
    }
    try:
        resp = await send_request(endpoint=API_ENDPOINTS["CHECK_GROUP_DETAILS"], data=payload)
        infoLogger.info(f"data : {resp}")
        team_leader = resp["data"]["attributes"]["team_leader"]
        vice_team_leader = resp["data"]["attributes"]["vice_team_leader"]
        batch_leader = resp["data"]["attributes"]["batch_leader"]
        db_member_list = resp["data"]["attributes"]["members"]
        description = ""
        if team_leader:
            description += f"Team Leader: {team_leader[0]}({team_leader[1]})\n"
        if vice_team_leader:
            description += f"Vice Team Leader: {vice_team_leader[0]}({vice_team_leader[1]})\n"
        if batch_leader:
            description += f"Batch Leader: {batch_leader[0]}({batch_leader[1]})\n"
        if len(db_member_list):
            description += "MEMBERS PRESENT IN SERVER :\n"
            not_in_group = "MEMBERS ABSENT IN SERVER :"
            for member in db_member_list:
                if member[1] in member_list.keys():
                    description += f"Name : {member[0]} ->>>> Id: {member[1]}\n"
                else:
                    not_in_group += f"\nName : {member[0]} ->>>> Id: {member[1]}"
            if not not_in_group.endswith("SERVER :"):
                description += (
                        f"\n {not_in_group} \n\n "
                        + "ASK THESE USERS TO JOIN THIS DISCORD SERVER,\n"
                        + " THEY WILL BE AUTOMATICALLY ADDED TO THIS GROUP"
                )
        return Embeds.success_embed(channel=message.channel, title="Team Details", description=description)
    except Exception as e:
        errorLogger.error(f"Error on fetching group details: {e}")


async def check_user_details(message, discord_id, show_mail=False):
    payload = {
        "data": {
            "attributes": {
                "discord_id": discord_id,
                "server_id":message.guild.id
            },
            "type": "users",
        }
    }
    try:
        resp = await send_request(endpoint=API_ENDPOINTS["CHECK_USER_DETAILS"], data=payload)
        user_detail = resp["data"]["attributes"]["user_details"][0]
        user_name = user_detail["name"]
        user_discord_id = user_detail["discord_id"]
        user_email = user_detail["email"]
        server_details = user_detail["server_details"]
        batch_leader_details = user_detail["batch_leader_details"]
        wait_list_details = user_detail["waitlisted"]

        embed = discord.Embed(title="User Details", color=0x00FF00)
        embed.add_field(name="Name", value=user_name, inline=False)
        embed.add_field(name="Discord ID", value=user_discord_id, inline=False)

        user = await message.guild.fetch_member(discord_id)
        if user:
            await fetch_roles(message.guild, user_detail, user)

        group_details = user_detail["group_details"]
        if group_details:
            group_section = ""
            for group_detail in group_details:
                group_name = group_detail["group_name"]
                server_name = group_detail["server_name"]
                server_link = group_detail["server_link"]
                group_type = group_detail["bootcamp_type"]

                group_section += f"Group Name: {group_name}\n"
                if server_name:
                    group_section += f"Group Server Name: {server_name}\n"
                if server_link:
                    group_section += f"Group Server Link: {server_link}\n"
                if group_type:
                    group_section += f"Group Type: {group_type.capitalize()}\n"

                group_section += "\n"

            embed.add_field(name="Group Details", value=group_section, inline=False)

        if server_details:
            embed.add_field(name="Member in Servers", value=", ".join(server_details), inline=False)
        if batch_leader_details:
            embed.add_field(name="Batch Leader of", value=", ".join(batch_leader_details), inline=False)
        if wait_list_details:
            embed.add_field(name="WaitListed", value="Yes" if wait_list_details else "No", inline=False)
        if user_email:
            embed.add_field(name="Connection Status", value="Connected with Website", inline=False)
            if show_mail:
                embed.add_field(name="Email", value=user_email, inline=False)
                await message.author.send(embed=embed)
        else:
            embed.add_field(name="Connection Status", value="Not Connected with Website", inline=False)

        await message.channel.send(embed=embed)

    except Exception as e:
        errorLogger.error(f"Error on fetching user details: {e}")


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


async def user_sync(message):
    try:
        user_ids = [str(user.id) for user in message.guild.members if not user.bot]
        total_users = len(user_ids)
        batch_size = 100
        num_batches = (total_users + batch_size - 1) // batch_size

        await message.channel.send(f"User synchronization started. Total users: {total_users}")
        await message.channel.send(
            f"Processing {num_batches} batch{'es' if num_batches > 1 else ''} for {batch_size} users per batch.")

        for batch_index in range(num_batches):
            batch_start = batch_index * batch_size
            batch_end = (batch_index + 1) * batch_size
            batch_user_ids = user_ids[batch_start:batch_end]

            try:
                user_details = await send_request(
                    endpoint=API_ENDPOINTS["CHECK_USER_DETAILS"],
                    data={
                        "data": {
                            "attributes": {
                                "discord_ids": batch_user_ids,
                            },
                            "type": "users",
                        }
                    },
                )
                infoLogger.info(f"Fetched user data for batch {batch_index + 1}")
                await sleep(1)

                for user_detail in user_details["data"]["attributes"]["user_details"]:
                    discord_id = user_detail["discord_id"]
                    user = await message.guild.fetch_member(discord_id)
                    await fetch_roles(message.guild, user_detail, user)

                await message.channel.send(f"Processed batch {batch_index + 1}/{num_batches}")
            except Exception as e:
                errorLogger.error(f"Error on fetching user on user-sync: {e}")

        await message.channel.send("User synchronization complete.")
    except Exception as e:
        errorLogger.error(f"Error on server sync: {e}")


async def fetch_roles(guild, user_detail, user):
    try:
        verified_role = discord.utils.find(lambda r: r.name == "Verified", guild.roles)
        verified = user_detail["verified"]
        group_details = user_detail["group_details"]
        batch_leader_details = user_detail["batch_leader_details"]

        if verified:
            if not discord.utils.find(lambda r: r.name == "Verified", user.roles):
                await user.add_roles(verified_role)
                infoLogger.info(f"Verified role ->>> {user.display_name}")
        else:
            if discord.utils.find(lambda r: r.name == "Verified", user.roles):
                await user.remove_roles(verified_role)
                infoLogger.info(f"Verified role taken ->>> {user.display_name}")
        user_groups = []

        if batch_leader_details:
            if not discord.utils.find(lambda r: r.name == "Batch Leader", user.roles):
                role = discord.utils.find(lambda r: r.name == "Batch Leader", guild.roles)
                await user.add_roles(role)
                infoLogger.info(f"Batch Leader role->>> {user.display_name}")
            for role_name in batch_leader_details:
                user_groups.append(role_name)
                role = discord.utils.find(lambda r: r.name == role_name, guild.roles)
                if role and not discord.utils.find(lambda r: r.name == role_name, user.roles):
                    await user.add_roles(role)
                    infoLogger.info(f"{role_name} role ->>> {user.display_name}")
                elif role:
                    infoLogger.info(f"Already has the {role_name} role ->>> {user.display_name}")

        for group_detail in group_details:
            group_name = group_detail["group_name"]
            user_groups.append(group_name)
            group_role = discord.utils.find(lambda r: r.name == group_name, guild.roles)
            if group_role:
                if not discord.utils.find(lambda r: r.name == group_name, user.roles):
                    await user.add_roles(group_role)
                    infoLogger.info(f"{group_name} role->>> {user.display_name}")
                else:
                    infoLogger.info(f"Already has the {group_name} role ->>> {user.display_name}")
        # Remove extra roles not in group details
        extra_roles = [role for role in user.roles if
                       role.name not in user_groups and role and role.name.startswith("V2") and role.name.endswith(
                           "Team")]
        if extra_roles:
            await user.remove_roles(*extra_roles)
            infoLogger.info(
                f"Removed extra roles: {', '.join(role.name for role in extra_roles)} ->>> {user.display_name}")
    except Exception as e:
        errorLogger.error(f"Error on fetching user on fetch roles: {e}")
