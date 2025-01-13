from pyexpat.errors import messages
from typing import Optional, Any, Dict

from rest_framework.views import exception_handler
from rest_framework import exceptions, status

from item_api.util import uuid_of

# uuid でリソースを特定するエンドポイント
path_item_dict: dict[str, str] = {
    'companies' : '企業',
    'categories' : 'カテゴリ',
}
def _get_path_translation(context: Dict[str, Any]) -> Optional[str]:
    path: str = context.get('request').build_absolute_uri()
    # path_item_dict のキーをチェック
    for key, value in path_item_dict.items():
        if f'/{key}/' in path or path.endswith(f'/{key}'):
            return value
    raise None

uuid_error_message = 'UUIDをパスパラメーターにセットしてください'
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        # カスタムエラーメッセージの処理
        if response.status_code == 404:
            api_name = _get_path_translation(context)
            pk = context.get('kwargs').get('pk', None)
            # uuid 形式の id 指定ではない場合にエラーメッセージを加工 (id は uuid である前提)
            if api_name is not None and pk is not None and uuid_of(pk) is None:
                message = uuid_error_message
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                message = f'指定された{_get_path_translation(context)}が存在しません'
                status_code = response.status_code
            response.data = {
                'message': message
            }
            response.status_code = status_code
        if response.status_code == 400:
            if "ErrorDetail(string='This field may not be null.', code='null')" in str(response.data):
                response.data = {
                    'message' : 'パラメーターが不足しています'
                }
    return response
