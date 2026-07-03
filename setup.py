#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup

# Package meta-data.
NAME = "tapsdk"
DESCRIPTION = "Tap strap python sdk"
URL = "https://github.com/TapWithUs/tap-python-sdk"
EMAIL = "support@tapwithus.com"
AUTHOR = "Tap systems Inc."

REQUIRED = [
    # linux reqs
    'bleak==0.6.4;platform_system=="Linux"',
    # macOS reqs
    'bleak==0.12.1;platform_system=="Darwin"',
    # Windows reqs
    'bleak;platform_system=="Windows"'
]


here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, "Readme.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()
with io.open(os.path.join(here, "History.md"), encoding="utf-8") as f:
    long_description += "\n\n" + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, NAME, "__version__.py")) as f:
    exec(f.read(), about)


setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=("tests", "examples", "docs")),
    install_requires=REQUIRED,
    include_package_data=True,
    license="MIT",
    python_requires='>=3.9',
    extras_require={
        "dev": ["pytest", "flake8"]
    },
    # classifiers=[
    #     # Trove classifiers
    #     # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    #     "Framework :: AsyncIO",
    #     "Intended Audience :: Developers",
    #     "Topic :: Communications",
    #     "License :: OSI Approved :: MIT License",
    #     "Operating System :: Microsoft :: Windows :: Windows 10",
    #     "Operating System :: MacOS :: MacOS X",
    #     "Programming Language :: Python",
    #     "Programming Language :: Python :: 3",
    #     "Programming Language :: Python :: 3.7",
    #     "Programming Language :: Python :: 3.8"
    # ],
)
