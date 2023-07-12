from asyncio import sleep

from logger import errorLogger, infoLogger

# from utils.config import CONFIG


async def notify_user(data, client):
    """
    notify the user of a verification role
    Args:
     - data, client
    """
    try:
        await client.login(data["payload"]["bot"])
        user = await client.fetch_user(data["payload"]["discord_id"])
        await user.send(data["payload"]["message"])
        infoLogger.info(f" send message to : {user.name}")
        await client.close()
    except (Exception) as e:
        errorLogger.error(f" error on notification: {data} error: {e}")


async def notify_mass_user(data, client):
    """
    notify mass users
    Args:
     - data, client
    """
    error_file = open("error.txt", "a")
    sucess_file = open("sucess.txt", "a")
    await client.login(data["payload"]["bot"])
    for discord_id in data["payload"]["discord_id"]:
        try:
            user = await client.fetch_user(int(discord_id))
            sucess_file.write(f" send message to : {user.name}-{discord_id}")
            sucess_file.write("\n")
            await user.send(data["payload"]["message"])
            infoLogger.info(f" send message to : {user.name}")
        except (Exception) as e:
            errorLogger.error(f" error on notification: {data} error: {e}")
            error_file.write(f"discord_id:{discord_id} error: {e}")
            error_file.write("\n")
    await client.close()
    await sleep(2)
