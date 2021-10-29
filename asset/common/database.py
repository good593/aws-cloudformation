import boto3, json, logging

import psycopg2
import psycopg2.extras

from constants import SQL_TYPE, DB_TYPE, get_bucket_pip_install_base
from exception import BaseError

__all__ = ["DatabaseMgmt"]

class DatabaseMgmt:
    def __init_variable(self):
        self.sql_type = SQL_TYPE.SELECT
        self.result = {"status": False, "data": None}

    def __init__(self, dbType: DB_TYPE):
        self.db_type = dbType
        self.__init_variable()

    def __get_aico_db_user_info(self) -> dict:
        result = None
        KEY_USER_INFO = "database/aico_db_user_info.json"

        s3 = boto3.resource("s3")
        obj = s3.Object(get_bucket_pip_install_base(), KEY_USER_INFO)
        aico_db_user_info = json.loads(obj.get()["Body"].read().decode("utf-8"))

        result = {
            "host": aico_db_user_info[self.db_type.name]["host"],
            "port": aico_db_user_info[self.db_type.name]["port"],
            "database": aico_db_user_info[self.db_type.name]["database"],
            "user": aico_db_user_info[self.db_type.name]["user"],
            "password": aico_db_user_info[self.db_type.name]["password"],
        }

        if (
            self.db_type is DB_TYPE.AICO_AURORA_POSTGRE
            and self.sql_type is SQL_TYPE.SELECT
        ):
            result["host"] = aico_db_user_info[self.db_type.name]["host_read"]

        return result

    def __get_dbconnect(self) -> object:

        db_user_info = self.__get_aico_db_user_info()

        return psycopg2.connect(
            database=db_user_info["database"],
            host=db_user_info["host"],
            port=db_user_info["port"],
            user=db_user_info["user"],
            password=db_user_info["password"]
        )

    def __convert_result(self, cursor: object) -> list:
        logging.debug("[aico_db][__convert_result] start")
        result = []
        try:
            fetchall = cursor.fetchall()
        except psycopg2.ProgrammingError as e:
            logging.debug("[aico_db][__convert_result] no return")
            return result
        if not len(fetchall):
            logging.debug("[aico_db][__convert_result] no data")
            return result

        headers = [x[0] for x in cursor.description]
        for row in fetchall:
            result.append(dict(zip(headers, row)))

        logging.debug("[aico_db][__convert_result] end")
        return result

    def __excute_sql(
        self, reqSQL: str, reqParams: tuple = None, is_many: bool = False
    ) -> list:
        self.result["status"] = True
        conn = None
        cursor = None

        try:

            conn = self.__get_dbconnect()

            with conn.cursor() as cursor:
                if self.sql_type is SQL_TYPE.SELECT:
                    if reqParams is not None:
                        logging.debug("[aico_db][__excute_sql] select and params")
                        cursor.execute(reqSQL, reqParams)
                    else:
                        logging.debug("[aico_db][__excute_sql] select and no params")
                        cursor.execute(reqSQL)

                    self.result["data"] = self.__convert_result(cursor)
                elif self.sql_type is SQL_TYPE.NO_SELECT:
                    if is_many and reqParams is not None:
                        logging.debug("[aico_db][__excute_sql] no select and many")
                        cursor.executemany(reqSQL, reqParams)
                    elif reqParams is not None:
                        logging.debug("[aico_db][__excute_sql] no select and params")
                        cursor.execute(reqSQL, reqParams)
                    else:
                        logging.debug("[aico_db][__excute_sql] no select and no params")
                        cursor.execute(reqSQL)

                    self.result["data"] = self.__convert_result(cursor)
                    conn.commit()
                else:
                    logging.debug("[aico_db][__excute_sql][Exception] Nothing")
                    raise Exception('[DatabaseMgmt][__excute_sql] Nothing')

        except Exception as error:
            logging.debug("[aico_db][__excute_sql][error]")
            logging.error(
                "[DatabaseMgmt][__excute_sql] Error while connecting to Aurora", error
            )
            self.result["status"] = False
            self.result[
                "data"
            ] = "[DatabaseMgmt][__excute_sql] Error while connecting to Aurora > error : {}".format(
                str(error)
            )
            if conn is not None:
                conn.rollback()

            raise BaseError()
        finally:
            if conn is not None:
                conn.close()

        return self.result

    def __set_sql_type(self, reqSQL: str):

        l_reqSQL = reqSQL.lower()
        for v in SQL_TYPE.NO_SELECT.value[1]:
            if l_reqSQL.find(v) != -1:
                self.sql_type = SQL_TYPE.NO_SELECT
                break

    def __excute_sql_many(self, reqSQL: list, reqParams: list) -> dict:

        if self.sql_type is SQL_TYPE.SELECT:
            self.result["status"] = False
            self.result[
                "data"
            ] = "[DatabaseMgmt][__excute_sql_many] if reqParams is list, reqSQL can only be insert or update or delete!!"
            return self.result

        return self.__excute_sql(reqSQL, reqParams, is_many=True)

    def do_sql(self, reqSQL: str, reqParams: object = None) -> dict:
        # 초기화
        self.__init_variable()
        self.__set_sql_type(reqSQL)
        logging.debug(json.dumps({
            "function_nm" : "aico_db.do_sql",
            "reqSQL" : reqSQL,
            "reqParams" : reqParams
        }))

        if reqParams is not None and isinstance(reqParams, type([])):
            return self.__excute_sql_many(reqSQL, reqParams)
        else:
            return self.__excute_sql(reqSQL, reqParams)
