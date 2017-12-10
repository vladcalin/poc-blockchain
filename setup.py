from setuptools import setup, find_packages

setup(
    name='poc-blockchain',
    version='0.0.1',
    description='Proof of concept - blockchain',
    packages=find_packages(),
    install_requires=[
        'cryptography', 'click'
    ],
    entry_points={
        'console_scripts': [
            'wallet = blockchain.cli.wallet:cli',
            'netnode = blockchain.cli.node:cli'
        ]
    }
)
