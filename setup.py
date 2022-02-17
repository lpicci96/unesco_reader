from setuptools import setup, find_packages

with open("README.md", 'r') as fh:
    long_description = fh.read()


setup(
    author="Luca Picci",
    author_email = "lpicci96@gmail.com",
    description="Python package to download UNESCO data",
    name="unesco_reader",
    version="0.0.1",
    packages=find_packages(include=['unesco_reader', 'unesco_reader.*']),
    install_requires=['pandas', 'requests'],
    python_requires='>=3.8',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url = "https://github.com/lpicci96/unesco_reader"
    
)
