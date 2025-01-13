from rest_framework import exceptions, status


class CustomBaseException(exceptions.APIException):
    """
    デフォルトのキーではなく、message をキーにしてエラーレスポンスを生成できるようにします。
    """

    def __init__(self, code=None):
        self.detail = {"message": self.default_detail}

        if code is not None:
            self.detail["code"] = code


class ConflictedException(CustomBaseException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, message: str):
        self.default_detail = message
        super().__init__()


class RequiredException(CustomBaseException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, item_name):
        self.default_detail = f"{item_name}は必須項目です"
        super().__init__()


class NoUpdateParameterException(CustomBaseException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, item_name):
        self.default_detail = f"{item_name}を指定してください"
        super().__init__()


class AllSameUpdateParameterException(CustomBaseException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self):
        self.default_detail = "変更前と後で差異がありません"
        super().__init__()


class PutNotAllowedException(CustomBaseException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    default_detail = "PUT は許可されていません。PATCH を利用してください。"
