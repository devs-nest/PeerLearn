# import asyncio
import json
import re
from asyncio import sleep

import aiocron
import boto3
import discord
from discord.ext import commands, tasks

from logger import errorLogger, infoLogger
from services.user import (
    check_scrum_details,
)
from utils.config import CONFIG
from utils.groups import create_group, delete_group, update_group
from utils.notify_user import notify_group
from utils.role_modifier import assign_mass_role, assign_role, take_mass_role, take_role

sqs = boto3.resource("sqs", region_name=CONFIG["AWS_REGION"], aws_access_key_id=CONFIG["AWS_ACCESS_KEY_ID"],
                     aws_secret_access_key=CONFIG["AWS_SECRET_ACCESS_KEY"])
queue = sqs.get_queue_by_name(QueueName=CONFIG["SQS_NAME"])


class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):

        print("Events cog online.")
        try:
            self.compile_events.start()
        except RuntimeError:
            print("Task loop is still running.")

    @aiocron.crontab('0 0 * * SAT')
    async def scrum_data(self):
        for guild in self.client.guilds:
            roles = []
            for role in guild.roles:
                if role.name.startswith("V2") and role.name.endswith("Team"):
                    roles.append(role)

            for role in roles:
                channel_name = "-".join(
                    str(x).lower() for x in re.sub(" +", " ", re.sub("[^a-zA-Z0-9 \n]", "_", role.name).split(" "))
                )
                text_channel = discord.utils.find(
                    lambda r: r.name == channel_name + "-channel", guild.text_channels
                )
                if text_channel:
                    await sleep(2)
                    await check_scrum_details(text_channel, role.name)

    @tasks.loop(seconds=10, reconnect=True)
    async def compile_events(self):
        infoLogger.info("Reading message from queue: {}".format(queue))

        for message in queue.receive_messages(MaxNumberOfMessages=9, VisibilityTimeout=100, WaitTimeSeconds=1):
            # Let the queue know that the message is process
            data = message.body
            data = json.loads(data)
            infoLogger.info("_________________________________________________________________________________")
            infoLogger.info("data: {}".format(data))
            queue.delete_messages(Entries=[{"Id": message.message_id, "ReceiptHandle": message.receipt_handle}])
            try:
                function = print
                if data["type"] == "role_modifier":
                    if data["payload"]["action"] == "add_role":
                        function = assign_role
                    elif data["payload"]["action"] == "delete_role":
                        function = take_role
                    elif data["payload"]["action"] == "add_mass_role":
                        function = assign_mass_role
                    elif data["payload"]["action"] == "delete_mass_role":
                        function = take_mass_role
                elif data["type"] == "group_modifier":
                    if data["payload"]["action"] == "create":
                        function = create_group
                    elif data["payload"]["action"] == "destroy":
                        function = delete_group
                    elif data["payload"]["action"] == "update":
                        function = update_group
                elif data["type"] == "group_notifier":
                    function = notify_group

                if data:
                    bot_guild = ""
                    for guild in self.client.guilds:
                        if str(data["payload"]["guild_id"]) == str(guild.id):
                            bot_guild = guild
                            break
                    if bot_guild:
                        await function(data, guild)
                    else:
                        errorLogger.error("Guild not found.")
            except Exception as e:
                errorLogger.error(f" error on: payload: {e}")


def setup(client):
    client.add_cog(Events(client))
