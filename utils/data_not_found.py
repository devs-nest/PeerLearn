from utils.embeds import Embeds


async def data_not_found(channel, title="Sorry, Invalid parameters has been passed"):
    Embeds.error_embed(
        channel=channel,
        title=title,
        description="Run `dn-help {command}` to get help with the command",
    )
