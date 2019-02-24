from setuptools import setup, find_packages
from os import path
# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-freeipa-auth-json',
    version='0.1.0dev1',  
    description='FreeIPA authentication for Django using FreeIPA JSON API',  
    long_description=long_description, 
    long_description_content_type='text/markdown', 
    url='https://github.com/puttsk/django-freeipa-auth',  
    author='Putt Sakdhnagool',
    author_email='putt.sakdhnagool@nectec.or.th', 
    classifiers=[ 
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='django freeipa authentication', 
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4',

    project_urls={ 
        'Bug Reports': 'https://github.com/puttsk/slurm-sbalance/issues',
        'Source': 'https://github.com/puttsk/slurm-sbalance/',
    },
)
