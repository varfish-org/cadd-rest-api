import re

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework.views import APIView

from restapi.models import AnnotateBackgroundJobStatus
from restapi.tasks import annotate_background_job


#: Regular expression to parse variants with.
RE_VAR = (
    r"^(?P<contig>[a-zA-Z0-9\._])+-(?P<pos>\d+)-"
    "(?P<reference>[ACGTN]+)-(?P<alternative>[ACGTN]+)$"
)


class AnnotateApiView(APIView):
    def post(self, *args, **kwargs):
        genomebuild = self.request.data.get("genome_build")
        data = {
            "genome_build": genomebuild,
            "cadd_release": self.request.data.get("cadd_release"),
            "variants": [
                _normalize_vars(var, genomebuild)
                for var in self.request.data.get("variant")
                if re.search(RE_VAR, var)
            ],
        }
        bgjob = AnnotateBackgroundJobStatus.objects.create(
            status="active", args=data, info={"cadd_rest_api_version": 0.1}
        )
        annotate_background_job.delay(bgjob.id)
        return JsonResponse({"result": "OK", "bgjob_id": bgjob.id})


class ResultApiView(APIView):
    def post(self, *args, **kwargs):
        try:
            bgjob = AnnotateBackgroundJobStatus.objects.get(id=self.request.data.get("bgjob_id"))
        except ObjectDoesNotExist as e:
            return JsonResponse({"result": "Background job does not exist."}, status=500)
        response = {
            "result": "OK",
            "status": bgjob.status,
            "scores": bgjob.scores,
            "args": bgjob.args,
            "info": bgjob.info,
        }
        if bgjob.status == "finished":
            bgjob.delete()
        return JsonResponse(response)


def _normalize_vars(var, genomebuild):
    """Normalize variants regarding the ``"chr"`` prefix."""
    if genomebuild == "GRCh37":
        return var[3:] if var.startswith("chr") else var
    return var if var.startswith("chr") else ("chr" + var)
