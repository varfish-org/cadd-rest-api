from django.db import models
import jsonfield


class AnnotateBackgroundJobStatus(models.Model):
    status = models.CharField(
        max_length=16, choices=[("active", "active"), ("finished", "finished")], default="active"
    )
    args = jsonfield.JSONField()
    scores = jsonfield.JSONField()
    info = jsonfield.JSONField()
