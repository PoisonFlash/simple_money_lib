from setuptools import setup, find_packages

setup(
    name="simple_money_lib",
    version="0.9.0",
    packages=find_packages(),  # Automatically find and include the package files
    include_package_data=True,
    package_data={"simple_money_lib": ["data/*.json"]},
    install_requires=[],
    extras_require={
        'dev': ['pytest', 'pandas', 'lxml'],
    },
    author="PoisonFlash",
    description="Thread-safe and parsing-friendly library for simple operations with moneys and currencies",
)
