import enum, os

__all__ = [
    "STAGE_TYPE",
    "get_bucket_pip_install_base",
    "PRODUCT_CODE",
    "DB_TYPE",
    "SQL_TYPE",
    "HTTP_METHOD",
    "API_TYPE",
    "API_ANAL_STATUS",
    "SLACK_CHANNEL",
]

# 공통 상수들
class STAGE_TYPE(enum.Enum):
    # values -> 아이디, 주석
    dev = (enum.auto(), "개발 환경")
    ops = (enum.auto(), "운영 환경")
    none = (enum.auto(), "정의되지 않은 환경")


def get_bucket_pip_install_base():
    return "{STAGE}-aico-pip-install-base".format(
        STAGE=os.environ.get("STAGE_TYPE", STAGE_TYPE.dev.name)
    )


class PRODUCT_CODE(enum.Enum):
    # values -> 아이디, 주석
    none = (enum.auto(), "없음")
    aicando = (enum.auto(), "AI 초등 상품 코드")
    nurikids = (enum.auto(), "AI 누리키즈 상품 코드")


# DB 상수들
class DB_TYPE(enum.Enum):
    # values -> 아이디, 주석
    AICO_REDSHIFT = (enum.auto(), "redshift(DW)")
    AICO_AURORA_POSTGRE = (enum.auto(), "aurora postgre(RDB)")


class SQL_TYPE(enum.Enum):
    # values -> 아이디, DML종류
    SELECT = (enum.auto(), ["select"])
    NO_SELECT = (enum.auto(), ["insert", "update", "delete", "nextval"])


# API 상수들
class HTTP_METHOD(enum.Enum):
    # values -> 아이디
    get = enum.auto()
    post = enum.auto()


class API_TYPE(enum.Enum):
    # values -> 아이디, 주석
    POST_CONCENTRATION = (enum.auto(), "Private 학습 집중도 분석 결과 저장")
    POST_PREDICTED_CORRECT_RATE = (enum.auto(), "Private 예상 정답률 분석 결과 저장")
    POST_SOLVING_HABIT = (enum.auto(), "Private 문항 풀이습관 분석 결과 저장")
    POST_FORGOTTEN_KU = (enum.auto(), "Private 기억률에 따른 개념유닛 추천 결과 저장")
    POST_MASTERY_RATE = (enum.auto(), "Private 이해도 분석 결과 저장")


class API_ANAL_STATUS(enum.Enum):
    # values -> 아이디, 주석
    COMPLETE = (enum.auto(), "분석 상태 : 완료")
    RUNNING = (enum.auto(), "분석 상태 : 진행중")
    FAIL = (enum.auto(), "분석 상태 : 오류")


# SNS 상수들
class SLACK_CHANNEL(enum.Enum):
    # values -> 아이디, 주석, 슬랙 채널 아이디, 쓰레드 메세지 사용 유무, blocks template
    aico_notice = (enum.auto(), "AI분석 파트 알림 채널", "C02422NEJ1K", False)
    aico_batch = (enum.auto(), "AI분석 파트 배치 채널", "C0200Q8L0KW", True)
    aico_service = (enum.auto(), "AI분석 파트 분석 서비스 채널", "C01V5HEMAUD", False)
    aico_bi = (enum.auto(), "AI분석 파트 BI 채널", "C01V5HA0E77", False)
