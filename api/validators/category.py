from rest_framework.exceptions import ValidationError


def _effective_value(attrs, serializer, field):
    """PATCH では attrs に含まれないフィールドがあるため、既存インスタンスの値で補う"""
    if field in attrs:
        return attrs[field]
    return getattr(serializer.instance, field, None)


class SameCompanyParentCategoryValidator:
    """親カテゴリは同じ企業に属していなければならない"""

    requires_context = True
    message = "親カテゴリは同じ企業のカテゴリを指定してください。"

    def __call__(self, attrs, serializer):
        parent = _effective_value(attrs, serializer, "parent_category")
        if parent is None:
            return
        company = _effective_value(attrs, serializer, "company")
        if parent.company_id != company.id:
            raise ValidationError({"parent_category": self.message})


class NoCircularParentCategoryValidator:
    """自分自身や自分の子孫を親にしてはならない（更新時のみ成立しうる）"""

    requires_context = True
    message = "自分自身またはその子孫を親カテゴリに指定することはできません。"

    def __call__(self, attrs, serializer):
        instance = serializer.instance
        if instance is None:
            return
        node = _effective_value(attrs, serializer, "parent_category")
        while node is not None:
            if node.pk == instance.pk:
                raise ValidationError({"parent_category": self.message})
            node = node.parent_category
