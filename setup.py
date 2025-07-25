"""Setup file for the package."""

from setuptools import setup, find_packages

with open("requirements.txt") as req_file:
    install_requires = req_file.read().splitlines()

with open("requirements_test.txt", "r") as req_file:
    test_requires = req_file.read().splitlines()

setup(
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=install_requires,
    url="https://github.com/Domin-co/suspension-can-interface",
    extras_require={
        "test": test_requires,
    }
)
