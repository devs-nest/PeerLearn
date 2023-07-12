import asyncio

from discord import Embed


class Embeds:
    @staticmethod
    def generic_embed(
        channel=None,
        title=Embed.Empty,
        description=Embed.Empty,
        image=Embed.Empty,
        color=Embed.Empty,
    ):
        """
        Create a generic discord embed and send to a channel if channel passed
        """
        embed = Embed(color=color, title=title, description=description, image=image)
        if not channel:
            return embed
        else:
            return asyncio.ensure_future(channel.send(embed=embed))

    @staticmethod
    def web_active_required_embed(channel=None):
        """
        Embed for when user needs to be active on website
        """
        return Embeds.warning_embed(
            channel=channel,
            title="You need be connected to our website!",
            description="Run command `dn-connect` and follow the instructions to connect",
        )

    @staticmethod
    def error_embed(
        channel=None,
        title=Embed.Empty,
        description=Embed.Empty,
        image=Embed.Empty,
    ):
        """
        Error Embed
        """
        return Embeds.generic_embed(
            channel=channel,
            title=f":exclamation: {title}",
            description=description,
            image=image,
            color=0xDC2626,
        )

    @staticmethod
    def warning_embed(
        channel=None,
        title="",
        description=Embed.Empty,
        image=Embed.Empty,
    ):
        """
        Warning Embed
        """
        return Embeds.generic_embed(
            channel=channel,
            title=f":warning: {title}",
            description=description,
            image=image,
            color=0xFBBF24,
        )

    @staticmethod
    def success_embed(
        channel=None,
        title="",
        description=Embed.Empty,
        image=Embed.Empty,
    ):
        """
        Success Embed
        """
        return Embeds.generic_embed(
            channel=channel,
            title=f":white_check_mark: {title}",
            description=description,
            image=image,
            color=0x10B981,
        )

    @staticmethod
    def info_embed(
        channel=None,
        title="",
        description=Embed.Empty,
        image=Embed.Empty,
    ):
        """
        Info Embed
        """
        return Embeds.generic_embed(
            channel=channel,
            title=f":information_source: {title}",
            description=description,
            image=image,
            color=0x2563EB,
        )

    @staticmethod
    def send_embed(channel, embed):
        """
        Send embed to a channel wrapped with asyncio.ensure_future
        """
        return asyncio.ensure_future(channel.send(embed=embed))
