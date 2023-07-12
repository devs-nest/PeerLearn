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

    @commands.command(help="Connect your discord account to our website")
    async def connect(self, message):
        try:
            response = await send_request(
                endpoint=API_ENDPOINTS["GET_TOKEN"],
                data={"data": {"attributes": {"discord_id": str(message.author.id)}}},
            )
            bot_token = response["data"]["attributes"]["bot_token"]
            if bot_token:
                return Embeds.info_embed(
                    channel=message.author,
                    title="Connect discord to website",
                    description=(
                        "1. Open our [website](https://devsnest.in) and login\n"
                        + "2. In profile page click connect with discord button\n"
                        + f"3. Paste `{bot_token}` as your token"
                    ),
                )
            else:
                return Embeds.success_embed(
                    channel=message.author,
                    title="Already connected to website",
                )
        except BadRequest:
            return Embeds.error_embed(title="An error occurred while processing the command", channel=message.author)


def setup(client):
    client.add_cog(User(client))
