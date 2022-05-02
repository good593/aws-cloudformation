import boto3, logging, json, os
import pandas as pd
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
  """
  https://stackoverflow.com/questions/36780856/complete-scan-of-dynamodb-with-boto3
  """
  result = None

  try:
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2', endpoint_url='http://dynamodb.ap-northeast-2.amazonaws.com')
    table = dynamodb.Table(pTableNm)
    last_evaluated_key = None

    while True:
      response = None
      if isinstance(pColumns, list):
        select_cols = ''
        for col in pColumns:
          select_cols += col + ','
        select_cols = select_cols[:-1]
        if last_evaluated_key:
          response = table.scan(ProjectionExpression=select_cols, ExclusiveStartKey=last_evaluated_key)
        else:
          response = table.scan(ProjectionExpression=select_cols)
      elif last_evaluated_key:
        response = table.scan(ExclusiveStartKey=last_evaluated_key)
      else:
        response = table.scan()

      if response:
        result = pd.json_normalize(response['Items'])
        last_evaluated_key = response.get('LastEvaluatedKey')
      if not last_evaluated_key:
        break

  except (ClientError, Exception) as e:
    logger.exception(f'[get_data_from_dynamdb] pTableNm: {str(pTableNm)}')
    logger.exception(f'[get_data_from_dynamdb] error: {str(e)}')
  return result


def os_mkdir(path):
  if not os.path.exists(path):
    os.mkdir(path)

def download_videos_from_s3(pS3Prefix: str, pLoginDt, pLogoutDt):
  DOWNLOAD_PREFIX = ''
  os_mkdir(DOWNLOAD_PREFIX)
  video_list = []

  s3_resource = boto3.resource('s3')
  bucket = ''
  service_bucket = s3_resource.Bucket(bucket)
  objects = service_bucket.objects.filter(Prefix=pS3Prefix)
  for obj in objects:
    try:
      tmp = {}
      path, filename = os.path.split(obj.key)
      service_bucket.download_file(obj.key, DOWNLOAD_PREFIX+filename)
      tmp['filename'] = filename
      tmp['file_path'] = DOWNLOAD_PREFIX+filename
      tmp['obj_key'] = obj.key

      video_list.append(tmp)
    except (FileNotFoundError, Exception) as e:
      logging.error(e)

  return video_list


def upload_image_to_s3(pFileObj, pKey):
  s3 = boto3.client('s3')
  bucket = ''
  s3.upload_file(pFileObj, bucket, pKey)

def upload_audio_to_s3(pFileObj, pKey):
  s3 = boto3.client('s3')
  bucket = ''
  s3.put_object(Bucket = bucket, Body = pFileObj, Key = pKey, ContentType = 'audio/mpeg')
