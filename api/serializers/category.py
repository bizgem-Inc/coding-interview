import uuid
from rest_framework import serializers
from api.models import Category


class CategoriesSerializer(serializers.ModelSerializer):
    """
    カテゴリ階層構造を管理するためのシリアライザー。
    循環参照の防止や、階層情報の付与など、高度なバリデーションと変換を行う。
    """
    
    parent_category_name = serializers.SerializerMethodField(read_only=True)
    depth = serializers.SerializerMethodField(read_only=True)
    parent_category_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        format='hex_verbose'
    )

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'parent_category_id',
            'parent_category_name',
            'depth',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'parent_category_name',
            'depth'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # マルチテナント分離を確実にするため、company_idのコンテキストを必須とする
        if 'company_id' not in self.context:
            raise RuntimeError("CategoriesSerializer must be initialized with 'company_id' in context.")

    def get_parent_category_name(self, obj: Category) -> str | None:
        return obj.parent_category.name if obj.parent_category else None

    def get_depth(self, obj: Category) -> int:
        """ルートからの階層深さを計算する (0-indexed)"""
        depth = 0
        current = obj.parent_category
        while current:
            depth += 1
            current = current.parent_category
        return depth

    def validate_parent_category_id(self, value: uuid.UUID | None) -> uuid.UUID | None:
        """
        親カテゴリIDの妥当性を検証する。
        - 同一企業内のカテゴリであること
        - 循環参照（自分自身や子孫を親にする）が発生しないこと
        """
        if value is None:
            return value

        company_id = self.context.get('company_id')
        
        # 1. 同一企業内のカテゴリかチェック
        parent_exists = Category.objects.filter(id=value, company_id=company_id).exists()
        if not parent_exists:
            raise serializers.ValidationError("Specified parent category does not exist within the company.")

        # 2. 循環参照の防止 (PATCH/PUT時)
        if self.instance and self.instance.pk:
            if value == self.instance.pk:
                raise serializers.ValidationError("A category cannot be its own parent.")
            
            # 設定しようとしている親を遡り、自分自身が現れないか確認
            current_parent = Category.objects.filter(id=value).first()
            while current_parent:
                if current_parent.id == self.instance.pk:
                    raise serializers.ValidationError("Circular reference detected: Target parent is a descendant of this category.")
                current_parent = current_parent.parent_category

        return value

    def to_internal_value(self, data):
        # parent_category_id をモデルの parent_category フィールドにマッピングするための調整
        ret = super().to_internal_value(data)
        if 'parent_category_id' in ret:
            parent_id = ret.pop('parent_category_id')
            if parent_id:
                ret['parent_category'] = Category.objects.get(id=parent_id)
            else:
                ret['parent_category'] = None
        return ret

    def to_representation(self, instance):
        # レスポンスでは parent_category_id としてIDを返す
        ret = super().to_representation(instance)
        ret['parent_category_id'] = instance.parent_category_id
        return ret
