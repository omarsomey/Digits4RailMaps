from setuptools import setup, find_packages
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='rectool',
    version='0.1.0',
    description='Video and GPS stream recording tool',
    long_description=long_description,
    author='Omar Somai',
    author_email='omar.somai@knorr-bremse.com',
    url='https://github.com/omarsomey/Digits4RailMaps',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Linux",
    ],
    python_requires='>=3.6',
)