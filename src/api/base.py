import json
import re
import traceback
from abc import ABCMeta
from logging import getLogger

from cerberus import Validator, errors
from rest_framework.response import Response
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

logger = getLogger("api")


class CommonValidationException(Exception):
    def __init__(self, message: str):
        self.__message = message

    @property
    def message(self):
        return self.__message

class ResourceNotFoundException(Exception):
    pass


class CerberusErrorHandler(errors.BasicErrorHandler):
    """
    Cerberus(入力値バリデーションライブラリ)メッセージの定義
    メッセージ定義を上書きする
    """

    def __iter__(self):
        pass

    messages = errors.BasicErrorHandler.messages.copy()
    messages[errors.REGEX_MISMATCH.code] = "許可されていない文字列です"
    messages[errors.MIN_VALUE.code] = "最小値を下回っています"
    messages[errors.MAX_VALUE.code] = "最大値を超えています"
    messages[errors.REQUIRED_FIELD.code] = "必須なフィールドです"
    messages[errors.EMPTY_NOT_ALLOWED.code] = "入力をしてください"
    messages[errors.BAD_TYPE.code] = "入力は{constraint}型で入力してください"
    messages[errors.MAX_LENGTH.code] = "入力可能な桁数を超えています"
    messages[errors.UNALLOWED_VALUE.code] = "許可されていない入力値です"


class CustomValidator(Validator):
    """
    Cerberosのカスタムバリデータ
    """

    def _validate_is_positive_integer(self, is_positive_integer, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        _re = re.compile(r"^\d+$", re.I)
        if is_positive_integer and value and not _re.match(value):
            self._error(field, "入力は数値で入力してください。")


class APIViewBase(APIView, metaclass=ABCMeta):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def schema():
        """
        bodyのバリデーション定義 小クラスで実装を行う
        """
        pass

    @staticmethod
    def validation_request(validation_schema, request):
        request_validator = CustomValidator(validation_schema, error_handler=CerberusErrorHandler)
        if not request_validator.validate(request):
            msg = ""

            def parse_dict(e_key, e_val, e_msg):
                for k, v in e_val.items():
                    if type(v) == str:
                        return e_msg + "[" + k + "=" + v + "]"
                    elif type(v) == dict:
                        return parse_dict(k, v, e_msg)
                    elif type(v) == list:
                        return parse(k, v[0], e_msg)

            def parse(e_key, e_val, e_msg):
                if type(e_val) == str:
                    return e_msg + "[" + str(e_key) + "=" + e_val + "]"
                elif type(e_val) == dict:
                    return parse_dict(e_key, e_val, e_msg)
                elif type(e_val) == list:
                    return parse(e_key, e_val[0], e_msg)

            for key in request_validator.errors:
                val = request_validator.errors[key]
                msg = parse(key, val, msg)

            raise CommonValidationException(message=msg)

    def post_business_logic(self) -> Response:
        pass

    def get_business_logic(self) -> Response:
        pass

    def put_business_logic(self) -> Response:
        pass

    def delete_business_logic(self) -> Response:
        pass

    def post(self, request, **kwargs):
        try:

            logger.info(request.body)

            self.validation_request(self.schema(), json.loads(request.body))
            response = self.post_business_logic()
            return response
        except json.decoder.JSONDecodeError as e:
            err_msg = traceback.format_exc()
            logger.warning(err_msg)
            return Response(
                data={"error_message": "invalid json"},
                status=HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except CommonValidationException as e:
            err_msg = traceback.format_exc()
            logger.error(err_msg)
            return Response(
                data={"error_message": e.message},
                status=HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except ResourceNotFoundException as e:
            err_msg = traceback.format_exc()
            logger.error(err_msg)
            return Response(
                data={"error_message": e.message},
                status=HTTP_404_NOT_FOUND,
            )
        except:
            err_msg = traceback.format_exc()
            logger.error(err_msg)
            return Response(
                data={
                    "error_message": "something critical error occurred",
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request, **kwargs):
        try:
            logger.info(request.body)
            response = self.get_business_logic()
            return response
        except ResourceNotFoundException:
            err_msg = traceback.format_exc()
            logger.error(err_msg)
            return Response(
                data={"error_message": "resource not found"},
                status=HTTP_404_NOT_FOUND,
            )
        except:
            err_msg = traceback.format_exc()
            logger.error(err_msg)
            return Response(
                data={
                    "error_message": "something critical error occurred",
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, **kwargs):
        try:
            logger.info(request.body)

            self.validation_request(self.schema(), json.loads(request.body))
            response = self.put_business_logic()
            return response
        except json.decoder.JSONDecodeError as e:
            err_msg = traceback.format_exc()
            logger.warning(err_msg)
            return Response(
                data={"error_message": "invalid json"},
                status=HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except CommonValidationException as e:
            err_msg = traceback.format_exc()
            logger.error(err_msg)
            return Response(
                data={"error_message": e.message},
                status=HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except ResourceNotFoundException:
            err_msg = traceback.format_exc()
            logger.error(err_msg)
            return Response(
                data={"error_message": "resource not found"},
                status=HTTP_404_NOT_FOUND,
            )
        except:
            err_msg = traceback.format_exc()
            logger.error(err_msg)
            return Response(
                data={
                    "error_message": "something critical error occurred",
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, **kwargs):
        try:
            logger.info(request.body)
            response = self.delete_business_logic()
            return response
        except ResourceNotFoundException as e:
            err_msg = traceback.format_exc()
            logger.error(err_msg)
            return Response(
                data={"error_message": e.message},
                status=HTTP_404_NOT_FOUND,
            )
        except:
            err_msg = traceback.format_exc()
            logger.error(err_msg)
            return Response(
                data={
                    "error_message": "something critical error occurred",
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
