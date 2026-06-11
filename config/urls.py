from django.http import HttpResponseBadRequest
from django.urls import include, path


def bad_request_view(_request):
    return HttpResponseBadRequest("Bad Request")


urlpatterns = [
    path("", bad_request_view, name="root"),
    path("api", bad_request_view, name="api_root"),
    path("api/", include("api.urls")),
]
