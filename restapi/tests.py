import os
import tempfile
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from restapi.models import AnnotateBackgroundJob
import uuid


class TestBase(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff


class TestAnnotateApiView(TestBase):
    """Tests for AnnotateApiView.
    """

    # Patching the CADD_SH variable to point to the CADD.sh mocking script.
    # This script will return a valid CADD file with made-up data.
    @patch("restapi.tasks.CADD_SH", os.path.join(os.getcwd(), "helpers", "CADD_mocker.sh"))
    def test_post_annotate_request(self):
        response = self.client.post(
            reverse("restapi:annotate-api"),
            {
                "genome_build": "GRCh37",
                "cadd_release": "v1.4",
                "variant": ["1-100-A-G", "1-200-C-T"],
            },
        )
        self.assertEqual(response.status_code, 200)
        # Check if object with this UUID exist in database
        AnnotateBackgroundJob.objects.get(uuid=response.json().get("uuid"))


class TestResultApiView(TestBase):
    """Tests for ResultApiView.
    """

    def test_bgjob_doesnt_exist(self):
        bgjob_uuid = str(uuid.uuid4())
        response = self.client.post(reverse("restapi:result-api"), {"bgjob_uuid": bgjob_uuid})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json().get("result"),
            "Background job with uuid {} does not exist.".format(bgjob_uuid),
        )

    # Patching the CADD_SH variable to point to the CADD.sh mocking script.
    # This script will return a valid CADD file with made-up data.
    @patch("restapi.tasks.CADD_SH", os.path.join(os.getcwd(), "helpers", "CADD_mocker.sh"))
    def test_bgjob_exists_and_returns_results(self):
        response = self.client.post(
            reverse("restapi:annotate-api"),
            {
                "genome_build": "GRCh37",
                "cadd_release": "v1.4",
                "variant": ["1-100-A-G", "1-200-C-T"],
            },
        )
        bgjob_uuid = response.json().get("uuid")
        response = self.client.post(reverse("restapi:result-api"), {"bgjob_uuid": bgjob_uuid})
        self.assertEqual(response.status_code, 200)
        scores = response.json().get("scores")
        self.assertEqual(scores["1-100-A-G"][1], 0.1)
        self.assertEqual(scores["1-200-C-T"][1], 0.2)
