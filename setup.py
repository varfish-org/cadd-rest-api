#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Installation driver (and development utility entry point) for cadd-rest-api.
"""

import os
import sys

from setuptools import setup, find_packages

import versioneer

__author__ = "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>"


def parse_requirements(path):
    """Parse ``requirements.txt`` at ``path``."""
    requirements = []
    with open(path, "rt") as reqs_f:
        for line in reqs_f:
            line = line.strip()
            if line.startswith("-r"):
                fname = line.split()[1]
                inner_path = os.path.join(os.path.dirname(path), fname)
                requirements += parse_requirements(inner_path)
            elif line != "" and not line.startswith("#"):
                requirements.append(line)
    return requirements


# Enforce python version >=3.4
if sys.version_info < (3, 4):
    print("At least Python 3.4 is required.\n", file=sys.stderr)
    sys.exit(1)

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = parse_requirements("requirements.txt")

setup(
    name="cadd_rest_api",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="CADD REST API",
    long_description=readme + "\n\n" + history,
    author="Manuel Holtgrewe",
    author_email="manuel.holtgrewe@bihealth.de",
    url="https://github.com/bihealth/cadd-rest-api",
    packages=find_packages(),
    package_dir={"cadd_rest": "cadd_rest"},
    entry_points={"console_scripts": (("cadd-rest-server=cadd_rest.api:main",),)},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords="bioinformatics, demultiplexing",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
