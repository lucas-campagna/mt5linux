from setuptools import find_packages, setup
setup(
    name='mt5linux',
    packages=find_packages(include=['mt5linux']),
    version='0.1.0',
    description='MetaTrader5 for linux users',
    author='Lucas Prett Campagna',
    license='MIT',
    install_requires=open('requirements.txt','r').read().split('\n'),
    setup_requires=[],
    tests_require=[],
    test_suite='tests',
)