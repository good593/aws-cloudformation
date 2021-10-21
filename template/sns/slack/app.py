import logging, json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

from slack_sns.main_slack import AICO_SLACK, AWS_LOG

def lambda_handler(event, context):
  logging.debug("[SLACK] event >> "+json.dumps(event, ensure_ascii=False) )

  aws_log = AWS_LOG(pEvent=event)
  slack_msgs = aws_log.get_slack_msgs()
  logging.debug("[SLACK] slack_channel_nm >> "+aws_log.slack_channel_nm )

  slack = AICO_SLACK(pSlackChannelNm=aws_log.slack_channel_nm)
  for msg in slack_msgs:
    slack.do_message(msg)
