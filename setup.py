from setuptools import setup, find_packages

setup(
    name="simple_money_lib",
    version="1.0.0",
    packages=find_packages(),  # Automatically find and include the package files
    install_requires=[],
    extras_require={
        'dev': ['pytest', 'pandas', 'lxml'],
    },
    author="PoisonFlash",
    description="Thread-safe and parsing-friendly library for simple operations with moneys and currencies",
)
