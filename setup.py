from setuptools import setup
import sys, os

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = open("VERSION").readline().strip()

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'tstoolbox >= 22.55.29.20',
]


setup(name='hspfbintoolbox',
    version=version,
    description=("Reads Hydrological Simulation Program - "
                 "FORTRAN binary files and prints to screen."),
    long_description=README,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      'Development Status :: 5 - Production/Stable',
      'Environment :: Console',
      'Intended Audience :: Developers',
      'Intended Audience :: End Users/Desktop',
      'License :: OSI Approved :: BSD License',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 3',
      'Topic :: Scientific/Engineering',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='hspf binary hydrologic',
    author='Tim Cera, P.E.',
    author_email='tim@cerazone.net',
    url='http://timcera.bitbucket.io/hspfbintoolbox/docsrc/index.html',
    packages=['hspfbintoolbox'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['hspfbintoolbox=hspfbintoolbox.hspfbintoolbox:main']
    },
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
)
