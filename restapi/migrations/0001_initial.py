# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-09-19 14:31
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AnnotateBackgroundJob",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "active"),
                            ("failed", "failed"),
                            ("finished", "finished"),
                        ],
                        default="active",
                        max_length=16,
                    ),
                ),
                ("args", jsonfield.fields.JSONField()),
                ("scores", jsonfield.fields.JSONField()),
                ("info", jsonfield.fields.JSONField()),
                ("message", models.CharField(max_length=512)),
            ],
        )
    ]