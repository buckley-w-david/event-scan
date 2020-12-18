from setuptools import find_packages, setup

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='event_scan',
    version='0.1.0',
    author='David Buckley',
    author_email='david@davidbuckley.ca',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'toml',
        'typer',
        'SQLAlchemy',
        'feedgen',
    ],
    entry_points = {
        'console_scripts': [
            'event-scan=event_scan.cli:app'
        ]
    }
)
