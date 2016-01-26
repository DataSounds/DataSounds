from setuptools import setup, find_packages, Command
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = '1.2.5'

install_requires = [
#    'sebastian',
    'six',
    'numpy'
]


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(name='DataSounds',
      version=version,
      description="Get music from Time Series data and other sequential data.",
      long_description=README,
      classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      ],
      keywords='Sonification Music Timeseries ',
      author='Arnaldo Russo, Luiz Irber',
      author_email='arnaldo@datasounds.org, luiz@datasounds.org',
      url='http://www.datasounds.org',
      license='BSD License',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      cmdclass={'test': PyTest},
      platforms='any',
      )
