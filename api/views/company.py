from rest_framework import mixins
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from api.models import Company
from api.serializers import CompanySerializer


class CompanyViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.order_by('name')

    def list(self, request):
        return super().list(request)

    def create(self, request):
        data = request.data
        company_serializer = CompanySerializer(data={
                'name': data.get('name'),
            })
        company_serializer.is_valid(raise_exception=True)
        company_serializer.save()

        return Response(status=status.HTTP_201_CREATED)


CompanyViewSet.__doc__ = '''

list:

Get the list of company

### Responses

#### **200 OK**

```json
[
    {
        "name": "Test",
        "created_at": "2025-01-30T02:17:44.603477Z",
        "updated_at": "2025-01-30T02:17:44.603678Z"
    },
    {
        "name": "Test1",
        "created_at": "2025-01-30T02:21:02.149054Z",
        "updated_at": "2025-01-30T02:21:02.149195Z"
    }
]
```
'''
