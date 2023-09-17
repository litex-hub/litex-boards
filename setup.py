#!/usr/bin/env python3

from setuptools import setup
from setuptools import find_packages


with open("README.md", "r") as fp:
    long_description = fp.read()


setup(
    name="litex-boards",
    version="2023.08",
    description="LiteX supported boards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Florent Kermarrec",
    author_email="florent@enjoy-digital.fr",
    url="http://enjoy-digital.fr",
    download_url="https://github.com/litex-hub/litex-boards",
    test_suite="test",
    license="BSD",
    python_requires="~=3.6",
    install_requires=["litex"],
    include_package_data=True,
    packages=find_packages(exclude=['test*']),
)
