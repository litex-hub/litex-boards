#!/usr/bin/env python3

from setuptools import setup
from setuptools import find_packages


setup(
    name="litex-boards",
    description="LiteX supported boards",
    author="Florent Kermarrec",
    author_email="florent@enjoy-digital.fr",
    url="http://enjoy-digital.fr",
    download_url="https://github.com/litex-hub/litex-boards",
    test_suite="test",
    license="BSD",
    python_requires="~=3.6",
    include_package_data=True,
    packages=find_packages(exclude=['test*']),
)
