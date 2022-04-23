import enum, os


# 공통 상수들
class STAGE_TYPE(enum.Enum):
    # values -> 아이디, 주석
    dev = (enum.auto(), "개발 환경")
    ops = (enum.auto(), "운영 환경")
    none = (enum.auto(), "정의되지 않은 환경")



