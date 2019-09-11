import re

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework.views import APIView

from restapi.models import AnnotateBackgroundJob
from restapi.tasks import annotate_background_job


#: Regular expression to parse variants with.
RE_VAR = (
    r"^(?P<contig>[a-zA-Z0-9\._])+-(?P<pos>\d+)-"
    "(?P<reference>[ACGTN]+)-(?P<alternative>[ACGTN]+)$"
)


class AnnotateApiView(APIView):
    """API view for annotating variants."""

    def post(self, *args, **kwargs):
        """Returns either a 500 status if object couldn't be created, or the uuid if object was created successfully."""
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
        try:
            bgjob = AnnotateBackgroundJob.objects.create(
                status="active", args=data, info={"cadd_rest_api_version": 0.1}, scores={}
            )
        except IntegrityError:
            return JsonResponse(
                {"result", "Can't create annotate background job object."}, status=500
            )
        annotate_background_job.delay(bgjob.uuid)
        return JsonResponse({"uuid": bgjob.uuid})


class ResultApiView(APIView):
    """API view for fetching & deleting annotation results."""

    def post(self, *args, **kwargs):
        """Returns either a 500 status if job object wasn't found, or a listing of the status of the job.
        Deletes entry if status is finished or failed, after retrieving the results.
        """
        try:
            bgjob = AnnotateBackgroundJob.objects.get(uuid=self.request.data.get("bgjob_uuid"))
        except ObjectDoesNotExist:
            # Return error if retrieving background job object failed.
            return JsonResponse(
                {
                    "result": "Background job with uuid {} does not exist.".format(
                        self.request.data.get("bgjob_uuid")
                    )
                },
                status=500,
            )
        # Prepare return data
        response = {
            "result": bgjob.message,  # Any further information about the job state
            "status": bgjob.status,  # `finished`, `failed`, `active`
            "scores": bgjob.scores,  # only filled when `finished` state is reached, otherwise empty
            "args": bgjob.args,  # arguments passed to annotate view
            "info": bgjob.info,  # information dictionary
        }
        # Delete object only if job is in `finished` or `failed` state & data will be delivered.
        if bgjob.status in ("finished", "failed"):
            bgjob.delete()
        return JsonResponse(response)


def _normalize_vars(var, genomebuild):
    """Normalize variants regarding the ``"chr"`` prefix."""
    if genomebuild == "GRCh37":
        return var[3:] if var.startswith("chr") else var
    return var if var.startswith("chr") else ("chr" + var)
