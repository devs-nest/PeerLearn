import asyncio
import json
import sched
import time

import boto3

from logger import errorLogger, infoLogger
from utils.config import CONFIG
from utils.notify_user import notify_user

s = sched.scheduler(time.time, time.sleep)
# Get the service resource
sqs = boto3.resource("sqs", region_name=CONFIG["AWS_REGION"])

# Get the queue
notifier_queue = sqs.get_queue_by_name(QueueName=CONFIG["NOTIFIER_SQS_NAME"])


def read_queue(notifier_queue, s, client):
    """
    read all messages from the sqs queue
    Args:
     - queue, s, client

    """
    # Process messages by printing out body and optional author name

    infoLogger.info("Reading message from queue: {}".format(notifier_queue))
    for message in notifier_queue.receive_messages(MaxNumberOfMessages=9, VisibilityTimeout=100, WaitTimeSeconds=1):
        # Let the queue know that the message is process
        data = message.body
        data = json.loads(data)
        infoLogger.info("data: {}".format(data))
        infoLogger.info("_________________________________________________________________________________")
        notifier_queue.delete_messages(Entries=[{"Id": message.message_id, "ReceiptHandle": message.receipt_handle}])
        try:
            loop = asyncio.get_event_loop()
            function = print
            if data["type"] == "notification":
                function = notify_user
            task = loop.create_task(function(data, client))
            loop.run_until_complete(task)
        except (Exception) as e:
            errorLogger.error(f" error on: payload: {e}")

    s.enter(5, 1, read_queue, (notifier_queue, s, client))


def shoot_sqs(client):
    """
    shoots an sqs client into a queue
    Args:
     - client
    """
    infoLogger.info("Shooting SQS")
    s.enter(5, 1, read_queue, (notifier_queue, s, client))
    s.run()
