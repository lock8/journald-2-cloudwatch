import ast
import codecs
import os

from setuptools import setup


class VersionFinder(ast.NodeVisitor):
    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        if node.targets[0].id == "version":
            self.version = node.value.s


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), "r", encoding="utf8").read()


def find_version(*parts):
    finder = VersionFinder()
    finder.visit(ast.parse(read(*parts)))
    return finder.version


setup(
    name="journald-2-cloudwatch",
    version=find_version("jd2cw", "version.py"),
    author="Noa backend team",
    author_email="backend@noa.one",
    description="Send journald logs to AWS CloudWatch",
    url="https://github.com/lock8/journald-2-cloudwatch",
    packages=("jd2cw",),
    install_requires=[
        "boto3==1.9.19",
        "click==8.1.7",
        "botocore==1.12.19",
    ],
    extras_require={
        "testing": [
            "pytest==6.2.5", "pytest-cov", "requests-mock==1.8.0", "flake8", "isort"
        ],
    },
    include_package_data=True,
    entry_points="""
    [console_scripts]
    jd2cw=jd2cw:main
    """
)
