from setuptools import setup, find_packages

setup(
    name="mt5linux",
    version="0.2.0",
    author="Lucas Prett Campagna",
    author_email="lucasprett129@gmail.com",
    description="MetaTrader5 for Linux users",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lucas-campagna/mt5linux",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13",
    install_requires=[
        "rpyc"
    ]
)