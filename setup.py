from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '1.0'

install_requires = [
    'sebastian',
    'numpy'
    ]


setup(name='DataSounds',
    version=version,
    description="Get music from Time Series data and other sequential data.",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='Sonification, Music, Time series, ',
    author='Arnaldo Russo, Luiz Irber',
    author_email='arnaldorusso@gmail.com, luiz.ierber@gmail.com',
    url='https://github.com/DataSounds/DataSounds',
    license='PSF',
    packages=find_packages('DataSounds'),
    package_dir = {'': 'DataSounds'},include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['DataSounds = datasounds.get_music']
    }
)
