import os

from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "BOT_TOKEN": os.getenv("BOT_TOKEN"),
    "LOG_CHANNEL": os.getenv("LOG_CHANNEL"),
    "ASK_A_BOT": os.getenv("ASK_A_BOT"),
    "BASE_URL": os.getenv("BASE_URL"),
    "TOKEN": os.getenv("TOKEN"),
    "SENTRY_URL": os.getenv("SENTRY_URL"),
    "KEEP_ALIVE": os.getenv("KEEP_ALIVE"),
    "PORT": os.getenv("PORT") or 8080,
    "AWS_REGION": os.getenv("AWS_REGION"),
    "SQS_NAME": os.getenv("SQS_NAME"),
    "NOTIFIER_SQS_NAME": os.getenv("NOTIFIER_SQS_NAME"),
    "VERIFICATION_ROLE": os.getenv("VERIFICATION_ROLE"),
    "DEVSNEST_GUILD_ID": os.getenv("DEVSNEST_GUILD_ID"),
    "NOTIFIER_BOT_TOKEN": os.getenv("NOTIFIER_BOT_TOKEN"),
    "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
}
