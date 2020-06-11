import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

exec(open('labbcat/version.py').read())

# This call to setup() does all the work
setup(
    name="nzilbb-labbcat",
    version=__version__,
    description="Client library for communicating with LaBB-CAT servers",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/nzilbb/labbcat-py/",
    author="Robert Fromont",
    author_email="robert@fromont.net.nz",
    license="GPL-3.0-or-later",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["labbcat"],
    include_package_data=False,
    install_requires=["requests"],
)
