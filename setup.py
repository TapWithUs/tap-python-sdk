#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup

# Package meta-data.
DISTRIBUTION_NAME = "tap-python-sdk"
PACKAGE_NAME = "tapsdk"
DESCRIPTION = "Tap strap python sdk"
URL = "https://github.com/TapWithUs/tap-python-sdk"
EMAIL = "support@tapwithus.com"
AUTHOR = "Tap systems Inc."

REQUIRED = [
    "bleak>=3.0.2,<4",
]


here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, "Readme.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()
with io.open(os.path.join(here, "docs", "release-notes.md"), encoding="utf-8") as f:
    long_description += "\n\n" + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, PACKAGE_NAME, "__version__.py")) as f:
    exec(f.read(), about)


setup(
    name=DISTRIBUTION_NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=("tests", "examples", "docs")),
    install_requires=REQUIRED,
    include_package_data=True,
    license="MIT",
    python_requires=">=3.10",
    extras_require={
        "dev": ["pytest", "flake8"]
    },
    classifiers=[
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "Topic :: Communications",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
)
