import sys

from pyspark.sql import SparkSession

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job

from layer.common.constants import *
from libs.script.common import *


def get_df_from_dynamodb(pGlueContext:GlueContext, pTableNm:str, pStage:str):
  
  dynamic_frame = pGlueContext.create_dynamic_frame.from_options(
    connection_type="dynamodb",
    connection_options={
        "dynamodb.input.tableName": "table_nm",
        "dynamodb.throughput.read.percent": "0.1",
        "dynamodb.splits": "1"
    }
  )
  df_dynamodb = dynamic_frame.toDF()

  df_dynamodb.cache()
  df_dynamodb.createOrReplaceTempView(pTableNm)
  return df_dynamodb

def save_df_to_s3(p_df, p_mode='overwrite'):
  # save
  bucket = "bucket_nm"
  batch_daily = "path"
  save_path = bucket + batch_daily
  
  p_df.write.mode(p_mode).format("parquet").save(save_path)
  # df_save.write.mode("append").format("parquet").save(save_path)


# params
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'p_product_code', 'p_target_dt', 'p_env'])
p_product_code = args['p_product_code']
p_env = args['p_env']
target_dt = args['p_target_dt']

# init
spark_session = SparkSession.builder.config("spark.sql.broadcastTimeout", "36000").getOrCreate()
glueContext = GlueContext(spark_session)
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

logger = glueContext.get_logger()
logger.info("start!!")

# 비지니스 코드

# job start!!
job.commit()
