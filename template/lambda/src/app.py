import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

from common.utils import *

def lambda_handler(event:dict, context:str) -> None:
  logging.debug("lambda_handler!!")