import io
import os
import re

from setuptools import find_packages
from setuptools import setup
import versioneer


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type("")
    with io.open(filename, mode="r", encoding="utf-8") as fd:
        return re.sub(text_type(r":[a-z]+:`~?(.*?)`"), text_type(r"``\1``"), fd.read())


setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    name="processor_tools",
    url="https://gitlab.npl.co.uk/eco/tools/processor_tools",
    license="None",
    author="Sam Hunt",
    author_email="sam.hunt@npl.co.uk",
    description="Tools to support the developing of processing pipelines",
    long_description=read("README.md"),
    packages=find_packages(exclude=("tests",)),
    install_requires=["numpy", "pyyaml", "pydantic", "python-dateutil"],
    extras_require={
        "dev": [
            "numpy",
            "pre-commit",
            "tox",
            "sphinx",
            "sphinx_book_theme",
            "sphinx_design",
            "sphinx_automodapi",
            "ipython",
            "pickleshare",
            "types-PyYAML",
        ]
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
