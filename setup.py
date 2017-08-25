from setuptools import setup, find_packages

setup(
    name='acescliui',
    version="1.0",
    description="ACES command line interface ui library",
    author="Jonathan Bachmann",
    packages=find_packages(exclude=['*.utils']),
    include_package_data=True
)
