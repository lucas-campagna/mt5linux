from setuptools import find_packages, setup
from pathlib import Path

base_dir = Path(__file__).parent

long_description = ""
if (base_dir / "README.md").exists():
    long_description = (base_dir / "README.md").read_text(encoding="utf-8")

install_requires = []
if (base_dir / "requirements.txt").exists():
    install_requires = (
        (base_dir / "requirements.txt").read_text(encoding="utf-8").strip().split("\n")
    )
    install_requires = [
        line.strip()
        for line in install_requires
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="mt5linux",
    packages=find_packages(include=["mt5linux"]),
    version="0.2.0",
    description="MetaTrader5 for linux users",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Lucas Prett Campagna",
    license="MIT",
    url="https://github.com/lucas-campagna/mt5linux",
    install_requires=install_requires,
    setup_requires=[],
    tests_require=[],
    test_suite="tests",
)
