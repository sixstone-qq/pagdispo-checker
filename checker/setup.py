"""Installer for aiven-checker
"""

import os.path
from setuptools import find_packages, setup


cwd = os.path.dirname(__file__)


setup(
    name='pagdispo-website-checker',
    description='Aiven based website checker',
    version='0.0.1',
    packages=find_packages('.'),
    install_requires=open(os.path.join(cwd, 'requirements.txt')).readlines(),
    test_require=open(os.path.join(cwd, 'requirements-test.txt')).readlines(),
    entry_points={
        'console_scripts': [
            'pagdispo-checker = pagdispo.checker.app:run',
        ]
    }
)
