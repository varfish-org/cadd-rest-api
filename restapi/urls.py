from django.conf.urls import url
from . import views


app_name = "restapi"

urlpatterns = [
    url(regex=r"^annotate/$", view=views.AnnotateApiView.as_view(), name="annotate-api"),
    url(regex=r"^result/$", view=views.ResultApiView.as_view(), name="result-api"),
]
