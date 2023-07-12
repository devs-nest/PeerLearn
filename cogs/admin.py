import re

import discord
from discord.ext import commands

from api.endpoints import API_ENDPOINTS
from api.request import send_request
from client import client
from logger import errorLogger, infoLogger
from services.user import check_channel_ask_a_bot
from services.user import assign_server, new_member_joined, user_sync
from utils.config import CONFIG
from utils.embeds import Embeds
from utils.groups import create_group, check_channel_category


# from utils.exception import BadRequest


class Admin(commands.Cog):
    def __init__(self, bt_client):
        self.client = bt_client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Admin cogs online.")

    @commands.command("sync", help="Super secret command only for admins")
    async def sync(self, message):
        # Only syncs user's username and discord id
        if not discord.utils.find(lambda r: r.name == "admin", message.author.roles):
            return Embeds.error_embed(channel=message.channel, title="Super secret command only for me")
        if await check_channel_ask_a_bot(message):
            for member in message.guild.members:
                if not member.bot and not discord.utils.find(lambda r: r.name == "Devsnest People", member.roles):
                    # infoLogger.info(member.bot)
                    try:
                        role = discord.utils.find(lambda r: r.name == "Devsnest People", member.guild.roles)
                        if role:
                            await member.add_roles(role)
                        await new_member_joined(member)
                        infoLogger.info(f"{member.name} has been added")
                        Embeds.success_embed(
                            channel=client.get_channel(int(CONFIG["LOG_CHANNEL"])),
                            title=f"{member.name} has been added",
                        )
                    except Exception as e:
                        errorLogger.error(f"Error while updating user status ERROR: {e}")

    @commands.command("create-team", help="Create team-role, Voice Channel, Text Channel")
    async def create_team(self, ctx, *team):
        if not discord.utils.find(lambda r: r.name == "admin", ctx.message.author.roles):
            return Embeds.error_embed(channel=ctx.message.channel, title="Super secret command only for me")
        try:
            role_name = " ".join(str(x) for x in team)
            guild = ctx.guild
            team_role = discord.utils.find(lambda r: r.name == role_name, guild.roles)
            if not team_role:
                team_role = await guild.create_role(name=role_name, mentionable=True)
                infoLogger.info("Team Role created")
            team_name = " ".join(str(x) for x in role_name.split(" "))
            team_channel_name = re.sub(" +", " ", re.sub("[^a-zA-Z0-9 \n]", "_", team_name))
            team_channel = "-".join(str(x).lower() for x in team_channel_name.split(" "))

            category = discord.utils.find(
                lambda r: r.name == "DN JUNE BATCH" and len(r.channels) < 48, guild.categories
            )

            # temp_voice_channel = discord.utils.find(
            #     lambda r: r.name == team_name + " Voice Channel", guild.voice_channels
            # )
            temp_text_channel = discord.utils.find(lambda r: r.name == team_channel + "-channel", guild.text_channels)

            if not temp_text_channel:
                temp_text_channel = await guild.create_text_channel(team_channel + "-channel", category=category)
                infoLogger.info(f'{team_channel + "-channel"} created')
            # if not temp_voice_channel:
            #     temp_voice_channel = await guild.create_voice_channel(team_name + " Voice Channel", category=category)
            #     infoLogger.info(f'{team_name + " Voice Channel"} created')
            await temp_text_channel.set_permissions(guild.default_role, view_channel=False)
            # await temp_voice_channel.set_permissions(guild.default_role, view_channel=False)
            await temp_text_channel.set_permissions(team_role, view_channel=True)
            # await temp_voice_channel.set_permissions(team_role, view_channel=True)

        except Exception as e:
            errorLogger.error(f" error on creating_group:  {e}")

    @commands.command("destroy-team", help="Destroy team-role, Voice Channel, Text Channel")
    async def destroy_team(self, ctx, *team):

        if not discord.utils.find(lambda r: r.name == "admin", ctx.message.author.roles):
            return Embeds.error_embed(channel=ctx.message.channel, title="Super secret command only for me")

        try:
            guild = ctx.guild
            team_name = " ".join(str(x) for x in team)
            team_role = discord.utils.find(lambda r: r.name == team_name, guild.roles)
            if team_role:
                await team_role.delete()
                infoLogger.info("Team Role destroy")

            # team_channel = "-".join(str(x).lower() for x in team)

            # temp_voice_channel = discord.utils.find(
            #     lambda r: r.name == team_name + " Voice Channel", guild.voice_channels
            # )
            # temp_text_channel = discord.utils.find(lambda r: r.name == team_channel + "-channel", guild.text_channels)
            # if temp_text_channel:
            #     await temp_text_channel.delete()
            #     infoLogger.info(f'{team_channel + "-channel"} destroyed')
            # if temp_voice_channel:
            #     await temp_voice_channel.delete()
            #     infoLogger.info(f'{team_name + " Voice Channel"} destroyed')

        except Exception as e:
            errorLogger.error(f" error on deleting_group:  {e}")

    @commands.command("update-team", help="Rename team-role, Voice Channel, Text Channel")
    async def update_team(self, ctx, *team):
        if not discord.utils.find(lambda r: r.name == "admin", ctx.message.author.roles):
            return Embeds.error_embed(channel=ctx.message.channel, title="Super secret command only for me")
        try:
            guild = ctx.guild
            old_name = " ".join(str(x) for x in team.split("|")[0])
            new_name = " ".join(str(x) for x in team.split("|")[1])

            team_role = discord.utils.find(lambda r: r.name == old_name, guild.roles)
            if team_role:
                await team_role.edit(name=new_name)
                infoLogger.info(f"{old_name} Updated to -->>> {new_name}")

            # old_team_name = " ".join(str(x) for x in old_name.split(" "))
            # new_team_name = " ".join(str(x) for x in new_name.split(" "))
            old_team_channel = "-".join(
                str(x).lower() for x in re.sub(" +", " ", re.sub("[^a-zA-Z0-9 \n]", "_", old_name).split(" "))
            )
            new_team_channel = "-".join(
                str(x).lower() for x in re.sub(" +", " ", re.sub("[^a-zA-Z0-9 \n]", "_", new_name).split(" "))
            )
            # temp_voice_channel = discord.utils.find(
            #     lambda r: r.name == old_team_name + " Voice Channel", guild.channels
            # )
            temp_text_channel = discord.utils.find(lambda r: r.name == old_team_channel + "-channel", guild.channels)
            if temp_text_channel:
                await temp_text_channel.edit(name=new_team_channel + "-channel")
                infoLogger.info(f'{old_team_channel + "-channel"} Updated to -->>> {old_team_channel + "-channel"}')
            # if temp_voice_channel:
            #     await temp_voice_channel.edit(name=new_team_name + " Voice Channel")
            #     infoLogger.info(
            #         f'{old_team_name + " Voice Channel"} Updated to -->>> {new_team_name + " Voice Channel"}'
            #     )

        except Exception as e:
            errorLogger.error(f" error on updating_group:  {e}")

    @commands.command("server-sync", help="Sync people with the server")
    async def server_sync(self, message):
        if not discord.utils.find(lambda r: r.name == "admin", message.author.roles):
            return Embeds.error_embed(channel=message.channel, title="Super secret command only for me")
        if await check_channel_ask_a_bot(message):
            for member in message.guild.members:
                if not member.bot:
                    try:
                        await assign_server(member)
                    except Exception as e:
                        errorLogger.error(f"Error while updating user status ERROR: {e}")

    @commands.command("group-sync", help="Sync all groups for the servers")
    async def group_sync(self, message):
        if not discord.utils.find(lambda r: r.name == "admin", message.author.roles):
            return Embeds.error_embed(channel=message.channel, title="Super secret command only for me")
        if await check_channel_ask_a_bot(message):
            server_groups = []
            # Get all groups of the server
            for channel in message.guild.channels:
                if channel.name.startswith("v2-"):
                    category_name = channel.category.name.split()[0] if channel.category else None
                    # Get roles with access to the channel
                    channel_role = ""
                    for overwrite in channel.overwrites:
                        if overwrite.name.startswith("V2"):
                            channel_role = overwrite.name
                            break

                    server_groups.append(
                        {'name': channel_role, 'channel_name': channel.name, 'bootcamp_type': category_name})
            # Get groups from backend
            infoLogger.info(f"data: {server_groups}")
            try:
                payload = {"data": {"attributes": {"server_id": message.guild.id}, "type": "groups"}}
                resp = await send_request(endpoint=API_ENDPOINTS["SERVER_GROUP"], data=payload)
                infoLogger.info(f"data: {resp}")
                db_groups = resp["data"]["attributes"]["groups"]
                db_group_names = [group["name"] for group in db_groups]
                server_group_names = [group["name"] for group in server_groups]

                # Create missing groups from the backend
                for group in db_groups:
                    if group["name"] not in server_group_names:
                        data = {'payload': {'group_name': [group["name"]], 'bootcamp_type': group["bootcamp_type"]}}
                        await create_group(data, message.guild)

                # Delete groups not present in the backend
                for group in server_groups:
                    if group["name"] not in db_group_names:
                        data = {'payload': {'group_name': [group["name"]]}}
                        # await delete_group(group["channel_name"], message.guild)
                        infoLogger.info(f"Deleting group: {group['channel_name']}")

                # Shift channels to correct categories based on bootcamp_type
                for group in db_groups:
                    data = {'payload': {'channel_name': group["channel_name"], 'bootcamp_type': group["bootcamp_type"]}}
                    await check_channel_category(data, message.guild)

            except (Exception) as e:
                errorLogger.error(f"Error on fetching groups: {e}")

    @commands.command("user-sync", help="Sync people with the server")
    async def user_sync(self, message):
        try:
            if not discord.utils.find(lambda r: r.name == "admin", message.author.roles):
                return Embeds.error_embed(channel=message.channel, title="Super secret command only for admins")
            if str(message.channel.name) == "admin-lane":
                await user_sync(message)
        except (Exception) as e:
            errorLogger.error(f"Error on server sync: {e}")

    @commands.command("delete-vc", help="Deletes all VC")
    async def delete_vc(self, message):
        if not discord.utils.find(lambda r: r.name == "admin", message.author.roles):
            return Embeds.error_embed(channel=message.channel, title="Super secret command only for me")
        if await check_channel_ask_a_bot(message):
            # Get groups from backend
            try:
                payload = {"data": {"attributes": {"server_id": message.guild.id}, "type": "groups"}}
                resp = await send_request(endpoint=API_ENDPOINTS["SERVER_GROUP"], data=payload)
                infoLogger.info(f"data : {resp}")
                db_groups = resp["data"]["attributes"]["groups"]
                for team_name in db_groups:
                    voice_channel = discord.utils.find(
                        lambda r: r.name == team_name + " Voice Channel", message.guild.voice_channels
                    )
                    if voice_channel:
                        await voice_channel.delete()
                        infoLogger.info(f"{team_name} Voice Channel deleted")
            except (Exception) as e:
                errorLogger.error(f" error on fetching_groups:  {e}")

    @commands.command("create-vc", help="Create all VC")
    async def create_vc(self, message):
        if not discord.utils.find(lambda r: r.name == "admin", message.author.roles):
            return Embeds.error_embed(channel=message.channel, title="Super secret command only for me")
        if await check_channel_ask_a_bot(message):
            # Get groups from backend
            try:
                payload = {"data": {"attributes": {"server_id": message.guild.id}, "type": "groups"}}
                resp = await send_request(endpoint=API_ENDPOINTS["SERVER_GROUP"], data=payload)
                infoLogger.info(f"data : {resp}")
                db_groups = resp["data"]["attributes"]["groups"]
                category = discord.utils.find(
                    lambda r: r.name == "DN JUNE BATCH" and len(r.channels) < 48, message.guild.categories
                )

                if not category:
                    errorLogger.error("Category not found")
                for team_name in db_groups:
                    team_role = discord.utils.find(lambda r: r.name == team_name, message.guild.roles)
                    voice_channel = discord.utils.find(
                        lambda r: r.name == team_name + " Voice Channel", message.guild.voice_channels
                    )
                    if not voice_channel:
                        voice_channel = await message.guild.create_voice_channel(
                            team_name + " Voice Channel", category=category
                        )
                        infoLogger.info(f'{team_name + " Voice Channel"} created')
                    await voice_channel.set_permissions(message.guild.default_role, view_channel=False)
                    await voice_channel.set_permissions(team_role, view_channel=True)
            except Exception as e:
                errorLogger.error(f" error on fetching_groups:  {e}")

    @commands.command("active-group", help="Get the active group")
    async def active_group(self, message):
        if not discord.utils.find(lambda r: r.name == "admin", message.author.roles):
            return Embeds.error_embed(channel=message.channel, title="Super secret command only for me")
        if await check_channel_ask_a_bot(message):
            # Get groups from backend
            try:
                resp = await send_request(endpoint=API_ENDPOINTS["ACTIVE_GROUPS"])
                infoLogger.info(f"data : {resp}")
                teams_with_slots = []
                for group in resp["data"]["attributes"]["result"]:
                    if group["members_count"] < 15:
                        teams_with_slots.append(group)
                description = ""
                i = 1
                for team in teams_with_slots:
                    description += (
                            f"{i}. [{team['group_name']}](https://devsnest.in/groups/{team['group_slug']})"
                            + f" has {team['members_count']} members\n"
                    )
                    if i % 10 == 0:
                        Embeds.success_embed(
                            channel=message.channel, title="Active Team Details with slots", description=description
                        )
                        description = ""
                    i += 1
                if description:
                    Embeds.success_embed(
                        channel=message.channel, title="Active Team Details with slots", description=description
                    )

            except Exception as e:
                errorLogger.error(f" error on fetching active groups:  {e}")


def setup(bt_client):
    bt_client.add_cog(Admin(bt_client))
