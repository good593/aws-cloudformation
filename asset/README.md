# 분석파트 공통 모듈
분석파트에서 공통으로 사용할 SNS, S3, DB 관련 개발을 통일하는 목적으로 생성함.
## 1. 설치 방법 & 업그레이드 방법
```bash
# python 3.8 이하만 사용 가능합니다.
(.venv) > pip install git+https://git-codecommit.ap-northeast-2.amazonaws.com/v1/repos/pip-install-base
```

## 2. 사용방법
### aico_utils 사용법
```python
from common.utils import camel_to_snake, snake_to_camel

# 사용법은 생략

```

### Exception 사용 방법
```python
from common.exception import AICOBaseError, aico_timeout
from common.constants import PRODUCT_CODE, SLACK_CHANNEL

import logging, os

# pSeconds : 타임아웃 설정 시간(초)
@aico_timeout(pProductCd=PRODUCT_CODE.aicando.name, pSlackChannelNm=SLACK_CHANNEL.aico_service.name, pSeconds=120)
def lambda_handler(event, context):
  os.environ['PRODUCT_CD'] = PRODUCT_CODE.aicando.name
  os.environ['SLACK_CHANNEL_NM'] = SLACK_CHANNEL.aico_service.name
  try:
    print("test")
    pServiceInfo = {
      "service_info": "서비스 정보"
    }
    
  except Exception as e:
    raise AICOBaseError()

```

## 3. 기타 
### [파일 설명](https://lsjsj92.tistory.com/592)
-  `__init__.py` 
> - 해당 Python 환경이 패키지라는 것을 알려줍니다.
> - Python package에서 사용하는 파일들의 정보를 담아두면 됩니다.
- `setup.py`
> - pip install을 할 때 사용되는 Python package setup 정보입니다.
> - name, description, version 등이 여기에 포함되어 있습니다. 
- https://ihopeido.tistory.com/entry/python-eggs-%EA%B0%84%EB%8B%A8%ED%95%9C-%EC%86%8C%EA%B0%9C
# [공통 개발자 가이드 문서](DeveloperGuide.md)