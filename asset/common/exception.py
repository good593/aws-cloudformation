import signal, json, logging, os

from functools import wraps
from constants import PRODUCT_CODE, SLACK_CHANNEL, STAGE_TYPE

__all__ = ["AICOBaseError", "aico_timeout"]

class AICOBaseError(Exception):
    def __set_environ_variables(self, pResult: json):
        logging.error("[__set_environ_variables] Start!!")
        if pResult["product_cd"] is None:
            pResult["product_cd"] = os.environ.get("PRODUCT_CD", PRODUCT_CODE.none.name)

        if pResult["slack_channel_nm"] is None:
            pResult["slack_channel_nm"] = os.environ.get(
                "SLACK_CHANNEL_NM", SLACK_CHANNEL.aico_notice.name
            )

        if (
            pResult["service_info"] is None
            and os.environ.get("SERVICE_INFO") is not None
        ):
            pResult["service_info"] = os.environ["SERVICE_INFO"]

        return pResult

    def __init__(
        self,
        pProductCd: str = None,
        pSlackChannelNm: str = None,
        pServiceInfo: json = None,
        pSeconds: int = 0,
    ) -> None:
        result = {
            "product_cd": pProductCd + " / " + os.environ.get("STAGE_TYPE", STAGE_TYPE.none.name),
            "slack_channel_nm": pSlackChannelNm,
            "service_info": pServiceInfo,
        }

        logging.error("[AICOBaseError] Start!!")
        ev_result = self.__set_environ_variables(result)

        if pSeconds > 0:
            ev_result["timeout_seconds"] = pSeconds

        str_ev_result = json.dumps(ev_result, ensure_ascii=False)
        logging.error("[AICOBaseError] >> " + str_ev_result)
        super().__init__(str_ev_result)


# timeout = 20분
def aico_timeout(
    pProductCd: str,
    pSlackChannelNm: str,
    pServiceInfo: json = None,
    pSeconds: int = 1200,
) -> object:
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise AICOBaseError(pProductCd, pSlackChannelNm, pServiceInfo, pSeconds)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.setitimer(signal.ITIMER_REAL, int(pSeconds))
            return func(*args, **kwargs)

        return wraps(func)(wrapper)

    return decorator
