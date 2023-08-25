import asyncio

from discord.ext import commands

from api.endpoints import API_ENDPOINTS
from api.request import send_request
from utils.embeds import Embeds
from utils.exception import BadRequest


class User(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command("hello", help="Says hello")
    async def hello(self, ctx):
        msg = f"Hello {ctx.author.mention}!"
        asyncio.ensure_future(ctx.channel.send(msg))

    @commands.command(help="Get your discord id")
    async def whoami(self, ctx):
        Embeds.info_embed(title="Your discord id:", description=f"`{ctx.author.id}`", channel=ctx.channel)


def setup(client):
    client.add_cog(User(client))
