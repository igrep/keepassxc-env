#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import os
import re

with open(os.path.join('keepassxc_env', '__init__.py'), 'r') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")


# Build the page that will be displayed on PyPI from the README and CHANGELOG
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()
long_description += "\n\n"
with open("CHANGELOG.md", encoding="utf-8") as f:
    long_description += f.read()
with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name="keepassxc-env",
    version=version,
    author="YAMAMOTO Yuji",
    author_email="igrep@n.email.ne.jp",
    description="A CLI to get environment variable from KeePassXC via keepassxc-proxy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/igrep/keepassxc-env",
    project_urls={
        "Issue tracker": "https://github.com/igrep/keepassxc-env/issues",
        "Changelog": "https://github.com/igrep/keepassxc-env/blob/master/CHANGELOG.md",
    },
    packages=["keepassxc_env"],
    zip_safe=True,
    entry_points={"console_scripts": ["keepassxc_env = keepassxc_env.__main__:main"]},
    install_requires=required,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
    ],
)
