import csv
import gzip
import os
import subprocess
import tempfile

from restapi.models import AnnotateBackgroundJobStatus
from config.celery import app
from config.settings.base import CADD_CONDA, CADD_ENV, CADD_SH, CADD_TIMEOUT


@app.task(bind=True)
def annotate_background_job(_self, bgjob_id):
    """Task to execute a CADD scoring background job."""
    bgjob = AnnotateBackgroundJobStatus.objects.get(id=bgjob_id)
    args = bgjob.args
    with tempfile.TemporaryDirectory(prefix="cadd_rest") as tmpdir:
        # Write out the input file for CADD.sh
        with open(os.path.join(tmpdir, "in.vcf"), "wt") as vcff:
            for variant in args["variants"]:
                print("%s\t%s\t.\t%s\t%s" % tuple(variant.split("-")), file=vcff)
        # Build command line to CADD.sh and execute.
        cmdline = [
            "bash",
            "-xc",
            (
                "{conda_activate}{cadd_sh} -a -g {genome_build} -v {cadd_release} "
                "-o {tmpdir}/out.tsv.gz {tmpdir}/in.vcf"
            ).format(
                conda_activate=("source %s; conda activate %s; " % (CADD_CONDA, CADD_ENV))
                if (CADD_CONDA and CADD_ENV)
                else "",
                cadd_sh=CADD_SH,
                genome_build=args["genome_build"],
                cadd_release=args["cadd_release"],
                tmpdir=tmpdir,
            ),
        ]
        proc = subprocess.Popen(cmdline)
        proc.wait(timeout=CADD_TIMEOUT)
        # Open CADD result file and create result.
        scores = {}
        with gzip.open(os.path.join(tmpdir, "out.tsv.gz"), "rt") as gzipf:
            reader = csv.reader(gzipf, delimiter="\t")
            header = None
            for row in reader:
                if not header and row and not row[0].startswith("#Chrom"):
                    continue
                elif not header and row and row[0].startswith("#"):
                    header = row
                elif header:
                    data = dict(zip(header, row))
                    key = "-".join((data[k] for k in ("#Chrom", "Pos", "Ref", "Alt")))
                    val = list(map(float, (data["RawScore"], data["PHRED"])))
                    scores[key] = val
        bgjob.scores = scores
        bgjob.status = "finished"
        bgjob.save()
