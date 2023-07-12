
import discord


def wrong_channel_prompt(desc):
    return discord.Embed(title="Oooooops! Seems like a Wrong channel :(", description=desc, ).set_thumbnail(
        url=("https://media.tenor.com/images/2b454269146fcddfdae60d3013484f0f/tenor.gif"))
