import csv
import gzip
import os
import subprocess
import sys
import tempfile

from flask import Flask
from flask_restplus import Resource, Api, reqparse, inputs

from cadd_rest import __version__

#: Regular expression to parse variants with.
RE_VAR = (
    r"^(?P<contig>[a-zA-Z0-9\._])+-(?P<pos>\d+)-"
    "(?P<reference>[ACGTN]+)-(?P<alternative>[ACGTN]+)$"
)

#: Host to bind to.
HOST = os.environ.get("HOST", "127.0.0.1")

#: Port to listen on.
PORT = int(os.environ.get("PORT", "8080"))

#: Path to ``CADD.sh`` file.
CADD_SH = os.environ.get("CADD_SH", "CADD.sh")

#: Path to conda installation.
CADD_CONDA = os.environ.get("CADD_CONDA", "")

#: Path to conda environment to activate for CADD if any.
CADD_ENV = os.environ.get("CADD_ENV", "cadd-env")

#: Timeout for CADD calls in seconds.
CADD_TIMEOUT = int(os.environ.get("CADD_TIMEOUT", "30"))

# Setup flask application with API.
app = Flask(__name__)
api = Api(app)


@api.route("/annotate", "/annotate/")
class Annotate(Resource):
    """The one and only API endpoint for annotating variants."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            "genome_build",
            choices=("GRCh37", "GRCh38"),
            required=True,
            help="Invalid genome build: {error_msg}",
        )
        self.parser.add_argument(
            "cadd_release",
            choices=("v1.4", "v1.5"),
            required=True,
            help="Invalid CADD release: {error_msg}",
        )
        self.parser.add_argument(
            "variant", type=inputs.regex(RE_VAR), dest="variants", action="append"
        )

    def get(self):
        return self._handle()

    def post(self):
        return self._handle()

    def _handle(self):
        """Handle GET and POST requests."""
        args = self._normalize_vars(self.parser.parse_args())
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
            result = {
                "args": args,
                "scores": scores,
                "info": {"cadd-rest-api-version": __version__},
            }
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
            return result

    def _normalize_vars(self, args):
        """Normalize variants regarding the ``"chr"`` prefix."""
        result = dict(args)
        if args["genome_build"] == "GRCh37":
            result["variants"] = [
                var[3:] if var.startswith("chr") else var for var in result["variants"]
            ]
        else:
            result["variants"] = [
                var if var.startswith("chr") else ("chr" + var) for var in result["variants"]
            ]
        return result


def main():
    print("Configuration\n", file=sys.stderr)
    print("HOST:         %s" % HOST, file=sys.stderr)
    print("PORT:         %s\n" % PORT, file=sys.stderr)
    print("CADD_SH:      %s" % CADD_SH, file=sys.stderr)
    print("CADD_CONDA:   %s" % CADD_CONDA, file=sys.stderr)
    print("CADD_ENV:     %s" % CADD_ENV, file=sys.stderr)
    print("CADD_TIMEOUT: %s" % CADD_TIMEOUT, file=sys.stderr)
    app.run(host=HOST, port=PORT)
