import sys

from pyspark.context import SparkContext

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job

from layer.common.constants import *
from libs.script.common import *

# params
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'p_product_code', 'p_target_dt', 'p_env'])
p_product_code = args['p_product_code']
p_env = args['p_env']
target_dt = args['p_target_dt']

# init
glueContext = GlueContext(SparkContext())
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

logger = glueContext.get_logger()
logger.info("start!!")

# 비지니스 코드

# job start!!
job.commit()
