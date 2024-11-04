from setuptools import setup, find_packages

setup(
    name='ysctlvpn',
    version='1.0',
    packages=find_packages(),  # This will automatically find all the packages (vpn, core, utils)
    entry_points={
        'console_scripts': [
            'ysctlvpn=vpn.ysctlvpn:main',  # Entry point that calls the 'main' function in ysctlvpn.py
        ],
    },
)
