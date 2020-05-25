from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='rectool',
    version='0.1.0',
    description='Video and GPS stream recording tool',
    long_description=readme,
    author='Omar Somai',
    author_email='omar.somai@knorr-bremse.com',
    url='https://github.com/omarsomey/Digits4RailMaps',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)