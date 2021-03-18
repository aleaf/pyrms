
import sys
from setuptools import setup
# To use:
#	   python setup.py bdist --format=wininst

from pyrms import __version__, __name__, __author__

if not sys.version_info[0] == 3:
    print('Sorry, pyrms only supports Python 3')
    print('  Your version of Python: {}'.format(sys.version))
    sys.exit(1)  # return non-zero value for failure

long_description = ''

try:
    import pypandoc

    long_description = pypandoc.convert('README.md', 'rst')
except:
    pass

setup(name=__name__,
      description='pyrms is a Python interface for working with PRMS models.',
      long_description=long_description,
      author=__author__,
      author_email='aleaf@usgs.gov',
      license='New BSD',
      platforms='Windows, Mac OS-X',
      install_requires=['numpy', 'pandas', 'shapely', 'gis-utils'],
      packages=['pyrms'],
      include_package_data=True, # includes files listed in MANIFEST.in
      # use this version ID if .svn data cannot be found
      version=__version__)