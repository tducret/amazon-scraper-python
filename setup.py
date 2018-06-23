# -*- coding: utf-8 -*-
from setuptools import setup
try:  # Pour pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # For pip <= 9
    from pip.req import parse_requirements

# Based on http://peterdowns.com/posts/first-time-with-pypi.html

__version__ = '0.0.9'  # Should match with __init.py__
_NOM_PACKAGE = 'amazonscraper'
_URL_GITHUB = 'https://github.com/tducret/amazon-scraper-python'
_DESCRIPTION = 'Package to search for products on Amazon and extract \
some useful information (title, ratings, number of reviews)'
_MOTS_CLES = ['api', 'amazon', 'python', 'amazonscraper', 'parsing',
              'python-wrapper', 'scraping', 'scraper', 'parser']
_SCRIPTS = ['amazon2csv.py']
# To delete here + 'scripts' dans setup()
# if no command is used in the package

install_reqs = parse_requirements('requirements.txt', session='hack')
requirements = [str(ir.req) for ir in install_reqs]

setup(
    name=_NOM_PACKAGE,
    packages=[_NOM_PACKAGE],
    package_data={},
    scripts=_SCRIPTS,
    version=__version__,
    license='MIT',
    platforms='Posix; MacOS X',
    description=_DESCRIPTION,
    long_description=_DESCRIPTION,
    author='Thibault Ducret',
    author_email='thibault.ducret@gmail.com',
    url=_URL_GITHUB,
    download_url='%s/tarball/%s' % (_URL_GITHUB, __version__),
    keywords=_MOTS_CLES,
    setup_requires=requirements,
    install_requires=requirements,
    classifiers=['Programming Language :: Python :: 3'],
    python_requires='>=3',
    tests_require=['pytest'],
)

# ------------------------------------------
# To upload a new version on pypi
# ------------------------------------------
# Make sure everything was pushed (with a git status)
# (or git commit --am "Comment" and git push)
# git tag 0.0.9 -m "Reliability improved : SSLError exception bypass"
# git push --tags

# Do a generation test on the pypi test repository
# python3 setup.py sdist register -r pypitest

# Upload test of the package on the pypi test repository
# python3 setup.py sdist upload -r pypitest

# Upload of the package on the official pypi repository
# python3 setup.py sdist upload -r pypi

# If you need to delete a tag
# git push --delete origin VERSION
# git tag -d VERSION
