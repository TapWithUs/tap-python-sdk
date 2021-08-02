#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

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
    'pythonnet;platform_system=="Windows"'
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


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPi via Twine…")
        os.system("twine upload dist/*")

        sys.exit()


setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=("tests", "examples", "docs")),
    # package_data={"tapsdk.backends.dotnet": ["*.dll"]},
    install_requires=REQUIRED,
    # test_suite="tests",
    # tests_require=TEST_REQUIRED,
    include_package_data=True,
    license="MIT",
    python_requires='>=3.7'
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
    # $ setup.py publish support.
    # cmdclass={"upload": UploadCommand},
)
