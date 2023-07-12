import discord
from discord.ext import commands

from utils.embeds import Embeds

intents = discord.Intents.all()  # trigger events for all
intents.members = True
intents.guilds = True
intents.presences = True
client = commands.Bot(command_prefix="dn-", intents=intents)

client.remove_command("help")


def command_help_short(command):
    return_text = ""
    prefix = client.command_prefix
    command_doc = command.short_doc or "No description"
    return_text += f"`{prefix}{command}`: {command_doc}\n"
    return return_text


def command_help_full(command):
    return_text = ""
    prefix = client.command_prefix
    command_params = ""
    for param in command.clean_params:
        command_params += "{" + param + "} "
    command_params = command_params.strip()
    command_doc = command.help or "No description"
    return_text += f"`{prefix}{command} {command_params}`\n{command_doc}".strip()
    return_text += "\n\n"
    return return_text


@client.command(name="help", help="Stuck? Run this to get help")
async def help(ctx, category_or_command=""):
    help_text = ""
    error = False

    # if user passed something like `dn-fetch`
    # remove `dn-` and keep the part after it
    category_or_command = category_or_command.lstrip("dn-")

    if category_or_command:
        # if user passed some category or command
        cog = client.get_cog(category_or_command)
        command = client.get_command(category_or_command)
        if client.get_cog(category_or_command):
            # if user passed some category
            help_text += f"\n**Commands in {category_or_command} Category -**\n"
            for command in cog.get_commands():
                if command.hidden:
                    continue
                help_text += command_help_full(command)
        elif command and not command.hidden:
            # if user passed some command
            help_text += f"\n**Usage of {category_or_command} command -**\n"
            help_text += command_help_full(command)
        else:
            # if user passed wrong category or command
            error = f"No category or command named `{category_or_command}` found"
    else:
        # if user passed nothing
        help_text += "The following commands are available:\n"
        for cog in client.cogs:
            help_text += f"\n**{cog} - **\n"
            for command in client.get_cog(cog).get_commands():
                if command.hidden:
                    continue
                help_text += command_help_short(command)
        help_text += "\nRun `dn-help {category}` or `dn-help {command}` to know more about a category or command"

    # check error and send the appropriate embed
    embed_type = Embeds.error_embed if error else Embeds.info_embed
    help_embed = embed_type(
        title=error or "PeerLearn Bot Help",
        description=(
            "Run `dn-help` to get list of all categories and commands"
            if error
            else (
                    "DN Bot is especially designed for the users of PeerLearn Community. "
                    "DN Bot is always there to help and make your learning fun. \n" + help_text
            )
        ),
    )
    if not ctx.author.dm_channel:
        await ctx.author.create_dm()
    await ctx.author.dm_channel.send(embed=help_embed)
