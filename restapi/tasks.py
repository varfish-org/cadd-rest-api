import csv
import gzip
import os
import subprocess  # nosec
import tempfile

from restapi.models import AnnotateBackgroundJob
from config.celery import app
from config.settings.base import CADD_CONDA, CADD_SH, CADD_TIMEOUT


@app.task(bind=True)
def annotate_background_job(_self, bgjob_uuid):
    """Task to execute a CADD scoring background job."""
    bgjob = AnnotateBackgroundJob.objects.get(uuid=bgjob_uuid)
    args = bgjob.args
    try:
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
                    conda_activate=("source %s; " % CADD_CONDA) if CADD_CONDA else "",
                    cadd_sh=CADD_SH,
                    genome_build=args["genome_build"],
                    cadd_release=args["cadd_release"],
                    tmpdir=tmpdir,
                ),
            ]
            # Submit the bash job
            proc = subprocess.Popen(
                cmdline, stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )  # nosec
            # Wait for the job or raise exception on timeout
            try:
                return_code = proc.wait(timeout=CADD_TIMEOUT)
            except subprocess.TimeoutExpired:
                # Write to job status to database on timeout and before raising.
                bgjob.status = "failed"
                bgjob.message = "Command line '{}' timed out after {} seconds limit.".format(
                    " ".join(cmdline), CADD_TIMEOUT
                )
                bgjob.save()
                raise
            # Check bash return code for validity, and raise exception if it is invalid.
            if return_code != 0:
                # Write job status to database before raising.
                bgjob.status = "failed"
                bgjob.message = "Command line '{}' exited with error code {} and message: {}".format(
                    " ".join(cmdline),
                    return_code,
                    " ".join(map(lambda x: x.decode(), proc.communicate())),
                )
                bgjob.save()
                raise subprocess.CalledProcessError(return_code, " ".join(cmdline))

            # Open CADD result file, create results and save them to database.
            scores = {}
            with gzip.open(os.path.join(tmpdir, "out.tsv.gz"), "rt") as gzipf:
                reader = csv.reader(gzipf, delimiter="\t")
                header = None
                for row in reader:
                    if not header and row and not row[0].startswith("#Chrom"):
                        continue
                    if not header and row and row[0].startswith("#"):
                        header = row
                    elif header:
                        data = dict(zip(header, row))
                        key = "-".join((data[k] for k in ("#Chrom", "Pos", "Ref", "Alt")))
                        val = list(map(float, (data["RawScore"], data["PHRED"])))
                        scores[key] = val
                # Save results to database
                bgjob.scores = scores
                bgjob.status = "finished"
                bgjob.message = "OK"
                bgjob.save()
    except IOError as e:
        # Return failed state if couldn't open file.
        bgjob.status = "failed"
        bgjob.message = e
        bgjob.save()
        raise e
