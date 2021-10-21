import enum

__all__ = ["SLACK_BLOCK_TYPE"]

class SLACK_BLOCK_TYPE(enum.Enum):
  DIVIDER = (enum.auto(), "구분자", {
    "type": "divider"
  })
  BUTTON = (enum.auto(), "버튼", {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "*Details of error message*"
    },
    "accessory": {
      "type": "button",
      "text": {
        "type": "plain_text",
        "text": "Link to AWS Cloudwatch"
      },
      "style": "danger",
      "url": "{MSG_LINK}"
    }
  })
  MESSAGE = (enum.auto(), "메세지", {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "{MESSAGE}"
    }
  })
  ERROR_MESSAGE = (enum.auto(), "에러 메세지", {
    "type": "context",
    "elements": [
      {
        "type": "mrkdwn",
        "text": "{ERROR_MSG}"
      }
    ]
  })
  SECTION = (enum.auto(), "기본 블럭 포멧", {
    "type": "section",
    "fields": [
      {"type": "mrkdwn", "text": "*Product Code / Stage:*\n {PRODUCT_CODE}"},
      {"type": "mrkdwn", "text": "*Occurred time:*\n {ERROR_TIME}"}
    ]
  })
  HEADER = (enum.auto(), "header 블럭 포멧", {
    "type": "header",
    "text": {"type": "plain_text", "text": "Occurred at:\n {SERVICE_NM}"},
  })