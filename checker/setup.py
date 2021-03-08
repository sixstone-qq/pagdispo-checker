"""Installer for aiven-checker
"""

from setuptools import find_packages, setup

setup(
    name='pagdispo-website-checker',
    description='Aiven based website checker',
    version='0.0.1',
    packages=find_packages('.'),
    entry_points={
        'console_scripts': [
            'pagdispo-checker = pagdispo.checker.app:run',
        ]
    }
)
