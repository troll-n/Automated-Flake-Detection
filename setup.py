from setuptools import find_packages, setup


def parse_requirements(file):
    with open(file, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


setup(
    name="Automated-Flake-Detection",
    version="0.1",
    packages=find_packages(),
    install_requires=parse_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            # if there are any scripts included in your package
        ],
    },
    author="Patrick Kaczmarek",
    author_email="pkaczmar@andrew.cmu.edu",
    description="Main repo for code related to the Automated Flake Detection project under Professor Sufei Shi, CMU Dept. of Physics",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rirert2/Automated-Flake-Detection",  # if exists
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
)
