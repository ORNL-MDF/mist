import os
from setuptools import setup

path = os.path.dirname(os.path.realpath(__file__))
requirement_path = os.path.join(path, "requirements.txt")
requires = []
with open(requirement_path) as f:
    requires = f.read().splitlines()

setup(
    name='mistlib',
    version='0.1.0',    
    description='A Python package for storing, sharing, and using information about materials in models and simulations.',
    url='https://code.ornl.gov/mist/mist',
    author='Stephen DeWitt, Gerry Knapp, Hope Spuck, Sam Reeve',
    author_email='dewittsj@ornl.gov',
    license='BSD 3-Clause',
    packages=['mistlib'],
    install_requires=requires,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License'
    ],
)
