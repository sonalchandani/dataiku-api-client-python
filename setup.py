#!/usr/bin/env python

from distutils.core import setup

VERSION = "2.1.0"

setup(
        name='dataiku-api-client',
        version=VERSION,
        license="MIT License",
        packages=["dataikuapi"],
        description="Python API client for Dataiku APIs",
        author="Dataiku",
        author_email="support@dataiku.com",
        url="https://www.dataiku.com"
     )