from setuptools import setup, find_packages
import sys

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

py_version = sys.version_info[:2]

if py_version < (3, 5):
    raise Exception("websockets requires Python >= 3.5.")

setup(
    name='pokemonai',
    version='0.0.1',
    description='Reinforcement Learning agent to play competitive Pokemon',
    long_description=readme,
    author='Rishi Shah',
    author_email='rishihahs@gmail.com',
    url='https://github.com/rishihahs/pokemonai',
    license=license,
    packages=find_packages(exclude=('bin')),
    package_data={
        'pokemonai': ['data/*.json']
    },
    entry_points={
        'console_scripts': [
            'pokemonai = pokemonai.__main__:main'
        ]
    },
)
