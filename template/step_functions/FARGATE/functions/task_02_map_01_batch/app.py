import os
import boto3
import json
import logging
import time
from botocore.config import Config


def lambda_handler(event, content):
  age = event['age'] * 10

  return {
    "name": event['name'],
    "age": age
  }


if __name__ == '__main__':
  # https://gonigoni.kr/posts/step-function-with-python/
  # https://stackoverflow.com/questions/55343073/is-there-a-way-to-retrieve-the-step-function-tasktoken-from-within-a-batch-job
  client = boto3.client('stepfunctions', config=Config(read_timeout=70), region_name=os.environ['REGION_NAME'])
  task_token = os.environ['TASK_TOKEN']

  try:

    client.send_task_heartbeat(taskToken=task_token)

    params = {
      'stage_type': os.environ['stage_type'],
      'name': os.environ['name'],
      'age': os.environ['age']
    }

    result = lambda_handler(params)
    client.send_task_success(taskToken=task_token, output=json.dumps(result))

  except Exception as e:
    client.send_task_failure(taskToken=task_token)
