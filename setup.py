from setuptools import setup

import os

_version_file_path = os.path.join(os.path.dirname(__file__), "sql_extended_objects", "version")
_readme_file_path = os.path.join(os.path.dirname(__file__), "README.md")

with open(_version_file_path) as f:
    __version__ = f.readline().strip()

with open(_readme_file_path, "rb") as f:
    readme = f.read().decode("utf-8")

setup(
    name="SQLExtendedObjects",
    version=__version__,
    install_requires=[],
    long_description="SQL Extended Objects",
    long_description_content_type="text/markdown",
    packages=["sql_extended_objects"],
    package_data={"sql_extended_objects": ["version"]},
    url="https://github.com/Ar4ikov/SQLExtendedObjects",
    license="MIT License",
    author="Nikita Archikov",
    author_email="bizy18588@gmail.com",
    description="Utilities and Classes for making easier work with SQLite Tables",
    keywords="opensource sql objects sqlite"
)
