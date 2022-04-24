import re, boto3, logging, json
import pandas as pd
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from datetime import datetime, timedelta
from dateutil import tz
from pytz import timezone
from io import BytesIO
from botocore.exceptions import ClientError

def json_load_s3(pKey:str, pBucket:str) -> list[dict]:
  s3 = boto3.resource("s3").Bucket(pBucket)
  return json.load(s3.Object(key=pKey).get()["Body"])

def json_dump_s3(pOjb:object, pBucket:str, pKey:str) -> dict:
  s3 = boto3.resource("s3").Bucket(pBucket)
  return s3.Object(key=pKey).put(Body=json.dumps(pOjb))


def save_json_to_s3(pDf:pd.DataFrame, pKey:str, pBucket:str) -> None:
  s3 = boto3.resource("s3").Bucket(pBucket)
  out_buffer = BytesIO()
  df_ = pDf.reset_index()
  df_.to_json(out_buffer, orient='records', compression='gzip')
  s3.Object(key=pKey).put(Body=out_buffer.getvalue())


def get_df_from_s3_parquets(prefix:str, pBucket:str) -> pd.DataFrame:
  bucket = pBucket
  result_df = pd.DataFrame()
  s3 = boto3.resource('s3').Bucket(bucket)

  for obj in s3.objects.filter(Prefix=prefix):
    try:
      body = obj.get()['Body'].read()
      temp = pd.read_parquet(BytesIO(body))
      result_df = pd.concat([result_df, temp])
    except:
      continue
  
  return result_df


def get_df_from_dynamodb(pTableNm:str, pColumns:list=None) -> pd.DataFrame:
  result = None

  try:
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2', endpoint_url='http://dynamodb.ap-northeast-2.amazonaws.com')
    table = dynamodb.Table(pTableNm)

    if isinstance(pColumns, list):
      select_cols = ''
      for col in pColumns:
        select_cols += col + ','
      select_cols = select_cols[:-1]
      response = table.scan(ProjectionExpression=select_cols)
    else:
      response = table.scan()

    result = pd.json_normalize(response['Items'])
  except (ClientError, Exception) as e:
    logger.exception(f'[get_data_from_dynamdb] pTableNm: {str(pTableNm)}')
    logger.exception(f'[get_data_from_dynamdb] error: {str(e)}')
  return result


def camel_to_snake(data: str) -> str:
  _name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", data)

  return re.sub("([a-z0-9])([A-Z])", r"\1_\2", _name).lower()

def snake_to_camel(data: str) -> str:
  REG = r"(.*?)_([a-zA-Z])"
  pattern = re.compile(REG)

  def __camel(match):
    return match.group(1) + match.group(2).upper()

  return pattern.sub(__camel, data, 0)

def get_yesterday(timeZone:str='Asia/Seoul') -> str:
	today = datetime.now(timezone(timeZone))
	return (today - timedelta(days = 1)).strftime('%Y-%m-%d')

def get_today(timeZone:str='Asia/Seoul') -> str:
	return datetime.now(timezone(timeZone)).strftime('%Y-%m-%d')

def get_targetdayTz(ptz: str, pTargetDay: str = None) -> str:
	defaul_zone = 'UTC'
	utc_zone = tz.gettz('UTC')
	target_zone = tz.gettz(ptz)
	
	if not pTargetDay:
		temp = datetime.strptime(get_yesterday(defaul_zone), '%Y-%m-%d').replace(tzinfo=utc_zone)
	else:
		temp = datetime.strptime(pTargetDay, '%Y-%m-%d').replace(tzinfo=utc_zone)
	
	return temp.astimezone(target_zone).strftime("%Y-%m-%d %H:%M:%S")