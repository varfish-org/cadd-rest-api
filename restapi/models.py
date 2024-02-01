import uuid

from django.db import models
import jsonfield

STATUS_ACTIVE = "active"
STATUS_FAILED = "failed"
STATUS_FINISHED = "finished"
STATUSES = [
    (STATUS_ACTIVE, STATUS_ACTIVE),
    (STATUS_FAILED, STATUS_FAILED),
    (STATUS_FINISHED, STATUS_FINISHED),
]


class AnnotateBackgroundJob(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=16, choices=STATUSES, default=STATUS_ACTIVE)
    args = jsonfield.JSONField()
    scores = jsonfield.JSONField()
    info = jsonfield.JSONField()
    message = models.CharField(max_length=512)
