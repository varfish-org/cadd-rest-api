from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

app_name = "restapi"

urlpatterns = [
    url(regex=r"^$", view=TemplateView.as_view(template_name="index.html")),
    url(regex=r"^annotate/$", view=views.AnnotateApiView.as_view(), name="annotate-api"),
    url(regex=r"^result/$", view=views.ResultApiView.as_view(), name="result-api"),
]
