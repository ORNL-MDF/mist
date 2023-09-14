from setuptools import setup

setup(
    name='mistlib',
    version='0.1.0',    
    description='A Python package for storing, sharing, and using information about materials in models and simulations.',
    url='https://code.ornl.gov/mist/mist',
    author='Stephen DeWitt',
    author_email='dewittsj@ornl.gov',
    license='ORNL Internal Software - Currently unlicensed',
    packages=['mistlib'],
    install_requires=['pandoc',              
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
    ],
)