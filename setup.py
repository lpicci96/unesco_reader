from setuptools import setup, find_packages

setup(
    author="Luca Picci",
    description="Python package to download UNESCO data",
    name="unesco_reader",
    version="0.1.0",
    packages=find_packages(include=["unesco_reader", "unesco_reader.*"]),
    install_requires=['pandas', 'requests'],
    python_requires='>3.8'
)
