from setuptools import setup, find_packages

setup(
    name='sandbox',
    version='0.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'external_hd_index = gcnr.sandbox.external_hd_index:main',
            'external_hd_query = gcnr.sandbox.external_hd_index:query',
            # TODO: ideally we want something like "external_hd query" (subcommands)
            'planetpython = gcnr.planetpython.planetpython_index:main',
        ]
    },
)
