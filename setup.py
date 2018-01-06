from setuptools import setup, find_packages

setup(
    name='pycoin',
    version='0.0.1',
    description='Proof of concept - blockchain',
    packages=find_packages(),
    install_requires=[
        'pynacl', 'click', 'peewee'
    ],
    entry_points={
        'console_scripts': [
            'pycoin-wallet = pycoin.wallet:cli',
            'pycoin-node = pycoin.node:cli'
        ]
    },
    extras_require={
        'dev': [
            'pytest', 'pytest-cov'
        ]
    }
)
