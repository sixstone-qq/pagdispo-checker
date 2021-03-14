"""Installer for aiven-recorder
"""

from setuptools import find_packages, setup

setup(
    name='pagdispo-website-recorder',
    description='Aiven based monitor website recorder',
    version='0.0.1',
    packages=find_packages('.'),
    entry_points={
        'console_scripts': [
            'pagdispo-recorder = pagdispo.recorder.app:run',
            'migrate-db = pagdispo.recorder.migration:run',
        ]
    }
)
