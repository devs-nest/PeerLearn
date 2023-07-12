import asyncio

from client import client


async def take_input_dm(user):
    try:

        def check(message):
            return message.channel == user.dm_channel and message.author == user

        user_input = await client.wait_for("message", check=check, timeout=60)

    except asyncio.TimeoutError:
        await user.send("Sorry, You didn't reply on time.")
        user_input = False

    return user_input
