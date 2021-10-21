import os, boto3, json, requests, copy, logging

from constants import (
    get_bucket_pip_install_base,
    API_TYPE,
    PRODUCT_CODE,
    STAGE_TYPE,
    HTTP_METHOD,
    API_ANAL_STATUS,
)

__all__ = ["RestfulapiMgmt"]

class RestfulapiMgmt:
    def __set_restfulapi_info(self):
        if self.os_stage == STAGE_TYPE.ops.name:
            BASE_URL = "https://e64okr6ib1-vpce-01bf19de36dcbb11f.execute-api.ap-northeast-2.amazonaws.com/ops/"
        else:
            BASE_URL = "https://sagp3ag5j0-vpce-01bf19de36dcbb11f.execute-api.ap-northeast-2.amazonaws.com/dev/"
        KEY = "restfulapi/aieco_restfulapi_info.json"

        s3 = boto3.resource("s3")
        obj = s3.Object(get_bucket_pip_install_base(), KEY)
        aieco_restfulapi_info = json.loads(obj.get()["Body"].read().decode("utf-8"))
        aieco_restfulapi_info["headers"]["product-code"] = self.product_cd.name

        if aieco_restfulapi_info:
            self.headers = aieco_restfulapi_info["headers"]
            self.api_url = BASE_URL + aieco_restfulapi_info[self.api_type.name][
                "api_url"
            ]
            self.http_method = aieco_restfulapi_info[self.api_type.name][
                "http_method"
            ].lower()
            self.insert_body = aieco_restfulapi_info[self.api_type.name]["insert_body"]
            self.update_body = aieco_restfulapi_info[self.api_type.name]["update_body"]
        else:
            logging.error(
                "[RestfulapiMgmt][__set_restfulapi_info] aieco_restfulapi_info is none"
            )

    def __init__(self, apiType: API_TYPE, productCd: PRODUCT_CODE):
        self.api_type = apiType
        self.product_cd = productCd
        self.key_product_cd = "productCode"
        self.key_analysis_status = "analysisStatus"
        self.is_update = False
        self.os_stage = os.environ.get("STAGE_TYPE", STAGE_TYPE.dev.name).lower()
        # set restfulapi info
        self.__set_restfulapi_info()

    def __validation_api(self, reqParams: dict, is_realtime: bool = True) -> bool:
        result = True

        if self.http_method == HTTP_METHOD.post.name and reqParams is None:
            result = False
        elif (
            self.is_update
            and reqParams[self.key_analysis_status] == API_ANAL_STATUS.RUNNING.name
        ):
            result = False
        elif (
            not self.is_update
            and is_realtime
            and reqParams[self.key_analysis_status] != API_ANAL_STATUS.RUNNING.name
        ):
            result = False

        return result

    def __excute_api(self, reqParams: str) -> dict:
        result = None

        if self.http_method == HTTP_METHOD.post.name:
            result = requests.post(
                self.api_url, data=json.dumps(reqParams), headers=self.headers
            )
        elif reqParams:
            result = requests.get(self.api_url, params=reqParams, headers=self.headers)
        else:
            result = requests.get(self.api_url, headers=self.headers)

        return result

    def __set_default_value(self, reParams: dict):
        # set Default value
        reParams[self.key_product_cd] = self.product_cd.name

    def get_insert_body(self) -> dict:
        # set Default value
        self.__set_default_value(self.insert_body)

        if self.key_analysis_status in self.insert_body.keys():
            self.insert_body[self.key_analysis_status] = API_ANAL_STATUS.RUNNING.name

        return self.insert_body

    def do_api_insert(self, insertParams: dict = None, is_realtime=True) -> dict:
        result = "[error] validation"
        if self.__validation_api(insertParams, is_realtime):
            # set Default value
            self.__set_default_value(insertParams)

            result = self.__excute_api(insertParams)
            if result.status_code == 200:
                self.insert_body = copy.deepcopy(insertParams)
                self.is_update = True

        return result

    def get_update_body(self) -> dict:

        return self.update_body

    def do_api_update(self, updateParams: dict = None) -> dict:
        result = None

        if self.is_update:
            update_body = copy.deepcopy(self.insert_body)
            for key in updateParams.keys():
                update_body[key] = updateParams[key]

            if self.__validation_api(update_body):
                # set Default value
                self.__set_default_value(update_body)
                result = self.__excute_api(update_body)

                if result.status_code == 200:
                    self.is_update = False

        return result
