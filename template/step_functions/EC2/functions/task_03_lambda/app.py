import logging, json

def lambda_handler(event, content):
  logging.info(json.dumps(event))
