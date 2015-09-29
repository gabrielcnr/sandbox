from setuptools import setup, find_packages

setup(
    name='sandbox',
    version='0.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'external_hd_index = gcnr.sandbox.external_hd_index:main',
        ]
    },
)
