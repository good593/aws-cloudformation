import re

from datetime import datetime, timedelta
from dateutil import tz
from pytz import timezone

def camel_to_snake(data: str) -> str:
  _name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", data)

  return re.sub("([a-z0-9])([A-Z])", r"\1_\2", _name).lower()

def snake_to_camel(data: str) -> str:
  REG = r"(.*?)_([a-zA-Z])"
  pattern = re.compile(REG)

  def __camel(match):
    return match.group(1) + match.group(2).upper()

  return pattern.sub(__camel, data, 0)

def get_yesterday(timeZone='Asia/Seoul'):
	today = datetime.now(timezone(timeZone))
	return (today - timedelta(days = 1)).strftime('%Y-%m-%d')

def get_today(timeZone='Asia/Seoul'):
	return datetime.now(timezone(timeZone)).strftime('%Y-%m-%d')

def get_targetdayTz(ptz: str, pTargetDay: str = None):
	defaul_zone = 'UTC'
	utc_zone = tz.gettz('UTC')
	target_zone = tz.gettz(ptz)
	
	if not pTargetDay:
		temp = datetime.strptime(get_yesterday(defaul_zone), '%Y-%m-%d').replace(tzinfo=utc_zone)
	else:
		temp = datetime.strptime(pTargetDay, '%Y-%m-%d').replace(tzinfo=utc_zone)
	
	return temp.astimezone(target_zone).strftime("%Y-%m-%d %H:%M:%S")