import os
from distutils.core import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
  name='django-selenium-panel',
  version='0.1.1',
  description='A Django panel to control Selenium testing on remote browsers',
  long_description=read('README.md'),
  url='https://github.com/moiseshiraldo/django-selenium-panel',
  author='Moises Hiraldo',
  author_email='moiseshiraldo@gmail.com',
  license='GNU General Public License v3.0',
  packages=['selenium_panel'],
  python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
  install_requires=[
        'Django>=1.8,<1.9',
        'celery>=3.1',
        'selenium',
        'requests'
    ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Testing',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 2.7',
    'Framework :: Django :: 1.8',
    'Environment :: Web Environment',
    'Natural Language :: English'
  ],
)
