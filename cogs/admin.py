import re

import discord
from discord.ext import commands



# from utils.exception import BadRequest


class Admin(commands.Cog):
    def __init__(self, bt_client):
        self.client = bt_client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Admin cogs online.")


def setup(bt_client):
    bt_client.add_cog(Admin(bt_client))
