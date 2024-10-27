from setuptools import setup, find_packages

setup(
    name="simple_money_lib",
    version="0.1.0",
    packages=find_packages(),  # Automatically find and include the package files
    install_requires=["py-moneyed"],
    extras_require={
        'dev': ['pytest', 'pandas', 'lxml'],
    },
    author="PoisonFlash",
    description="Extend 'py-moneyed' functionalities for parsing and currency contexts",
)
