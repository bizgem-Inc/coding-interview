from django.shortcuts import get_object_or_404

from rest_framework import mixins
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from api.models import Category
from api.models import Company
from api.serializers import CategorySerializer

import uuid

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

class CategoryViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.order_by('name')
    lookup_field = 'id'

    def list(self, request):
        return super().list(request)

    def create(self, request):
        data = request.data
        catergory_serializer = CategorySerializer(data={
                'company': data.get('company'),
                'name': data.get('name'),
                'parent_category': data.get('parent_category'),
            })
        catergory_serializer.is_valid(raise_exception=True)
        catergory_serializer.save()

        return Response(status=status.HTTP_201_CREATED)

    def retrieve(self, request, id=None):
        if (is_valid_uuid(id)):
            try:
                category = Category.objects.get(id=id)
            except Category.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = CategorySerializer(category)

            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, id):
        data = request.data
        if (is_valid_uuid(id)):
            try:
                company_obj = Company.objects.get(id=data.get('company'))
                parent_category_obj = None;
                if (data.get('parent_category')):
                    parent_category_obj = Category.objects.get(id=data.get('parent_category'))
                category = Category.objects.get(id=id)
                category.company = company_obj
                category.name = data.get('name')
                category.parent_category = parent_category_obj
                category.save()
            except Category.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = CategorySerializer(category)

            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, id):
        data = request.data
        if (is_valid_uuid(id)):
            try:
                category = Category.objects.get(id=id)
                category.delete()
            except Category.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

CategoryViewSet.__doc__ = '''

list:

Get the list of category

### Responses

#### **200 OK**

```json
[
    {
        "id": "cad8c7ab-ff92-48b6-bb44-1434a85fe853",
        "company": "5fa93e39-f58f-42a6-9852-dee50596b276",
        "name": "Test",
        "parent_category": null,
        "created_at": "2025-01-30T02:27:08.081168Z",
        "updated_at": "2025-01-30T02:27:08.081303Z"
    }
]
```
'''
