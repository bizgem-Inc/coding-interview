import uuid
from django.db import models
from django.core.exceptions import ValidationError
from .base import LtreeField, BaseModel
from .company import Company

# ltreeの制限: ラベル長255文字、パス全体65535バイト、最大階層65535
# UUID hex(32文字) + ドット(1文字) = 33文字/階層
# 実用的な制限として最大10階層までとする
MAX_DEPTH = 10


class Category(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company, related_name="+", on_delete=models.CASCADE, db_comment="企業ID"
    )
    name = models.CharField(max_length=255, db_comment="カテゴリ名")
    parent_category = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
        db_comment="親カテゴリID",
    )
    # カスタムLtreeフィールドを使用
    path = LtreeField(
        db_index=True,
        db_comment="マテリアライズドパスを使用したltree型",
        editable=False,
    )

    def __str__(self):
        return self.name

    def clean(self):
        # 自己参照やループを防止
        if self.parent_category and self.parent_category_id == self.id:
            raise ValidationError("カテゴリに自分自身を親として設定できません。")

        # 階層の深さをチェック
        if self.parent_category:
            parent_depth = self.parent_category.get_depth()
            if parent_depth >= MAX_DEPTH:
                raise ValidationError(
                    f"カテゴリの階層は最大{MAX_DEPTH}レベルまでです。"
                    f"現在の親カテゴリはすでに{parent_depth}レベルです。"
                )

        ancestor = self.parent_category
        while ancestor:
            if ancestor.id == self.id:
                raise ValidationError("カテゴリの階層にループが含まれています。")
            ancestor = ancestor.parent_category

    def save(self, *args, **kwargs):
        # 子供のpath値は親のpath値に自分のid(hex)を連結して構築
        if self.parent_category:
            # 親のpathが保存済みでない場合、保存を走らせるかリロードする必要があります
            if not self.parent_category.path:
                self.parent_category.save()
            self.path = f"{self.parent_category.path}.{self.id.hex}"
        else:
            self.path = self.id.hex

        # 保存前にバリデーション（path以外のフィールド）を実行
        self.full_clean(exclude=["path"])
        super().save(*args, **kwargs)

    def get_ancestors(self):
        """祖先カテゴリを取得するヘルパー関数（ltree演算子を使用）"""
        if not self.path:
            return Category.objects.none()

        # @> 演算子: 左辺が右辺を含む（祖先を探す）
        return Category.objects.extra(
            where=["path @> %s AND path != %s"], params=[self.path, self.path]
        ).order_by("path")

    def get_descendants(self):
        """子孫カテゴリを取得するヘルパー関数"""
        if not self.path:
            return Category.objects.none()

        # PostgreSQLのltree演算子を使用して子孫を取得
        # <@ 演算子: 左辺が右辺に含まれる（path <@ self.path で、pathがself.pathの子孫）
        return Category.objects.extra(
            where=["path <@ %s AND path != %s"], params=[self.path, self.path]
        ).order_by("path")

    def get_depth(self):
        """階層の深さを取得"""
        if not self.path:
            return 0
        # ルートカテゴリ（親なし）は depth = 0、子は depth = 1、孫は depth = 2...
        return len(self.path.split(".")) - 1

    def get_siblings(self, include_self=False):
        """同じ親を持つ兄弟カテゴリを取得"""
        if self.parent_category:
            siblings = self.parent_category.children.all()
        else:
            siblings = Category.objects.filter(company=self.company, parent_category__isnull=True)

        if not include_self:
            siblings = siblings.exclude(id=self.id)

        return siblings.order_by("name")

    def is_ancestor_of(self, other):
        """他のカテゴリの祖先かどうかを判定（ltree演算子を使用）"""
        if not self.path or not other.path:
            return False

        # @> 演算子: 左辺が右辺を含む（祖先関係）
        return (
            Category.objects.filter(id=self.id)
            .extra(where=["path @> %s"], params=[other.path])
            .exists()
        )

    def is_descendant_of(self, other):
        """他のカテゴリの子孫かどうかを判定（ltree演算子を使用）"""
        if not self.path or not other.path:
            return False

        # <@ 演算子: 左辺が右辺に含まれる（子孫関係）
        return (
            Category.objects.filter(id=self.id)
            .extra(where=["path <@ %s"], params=[other.path])
            .exists()
        )

    def get_root(self):
        """ルートカテゴリを取得"""
        if not self.path:
            return None

        root_id = self.path.split(".")[0]
        return Category.objects.get(id=uuid.UUID(hex=root_id))

    @classmethod
    def get_tree_for_company(cls, company):
        """企業の全カテゴリをツリー構造で効率的に取得"""
        return cls.objects.filter(company=company).order_by("path")

    class Meta:
        db_table = "categories"
        db_table_comment = "カテゴリテーブル"
        verbose_name = "category"
        verbose_name_plural = "categories"
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(parent_category=models.F("id")),
                name="prevent_self_parent",
            ),
            models.UniqueConstraint(
                fields=["company", "name"], name="unique_company_category_combination"
            ),
        ]
        indexes = [
            models.Index(fields=["company", "name"]),
            models.Index(fields=["path"]),
        ]
