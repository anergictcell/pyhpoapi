import setuptools
import pyhpoapi
from pyhpoapi import config

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]

PACKAGES = (
    'pyhpoapi',
    'pyhpoapi.routers'
)

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Healthcare Industry',
    'Intended Audience :: Science/Research',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Scientific/Engineering :: Medical Science Apps.',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
]


setuptools.setup(
    name='pyhpoapi',
    version=config.VERSION,
    author='CENTOGENE GmbH',
    author_email="jonas.marcello@centogene.com",
    description="A HTTP REST API to work with the HPO Ontology",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/Centogene/pyhpoapi",
    packages=PACKAGES,
    classifiers=CLASSIFIERS,
    python_requires='>=3.6',
    include_package_data=True,
    install_requires=requirements
)
