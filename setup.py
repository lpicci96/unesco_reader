# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 15:51:04 2022

@author: lpicc
"""

from setuptools import setup, find_packages


setup(
      author="Luca Picci",
      description="Python package to download UNESCO data",
      name="unesco",
      version = "0.1.0",
      packages=find_packages(include = ["unesco", "unesco.*"]),
      install_requires=['pandas', 'requests'],
      python_requires='>3.8'
      )