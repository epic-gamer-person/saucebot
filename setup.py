from setuptools import setup

setup(
  name='saucebot',
  version='0.1',
  description='Reddit Bot',
  url='https://github.com/ranthai/saucebot',
  author='ranthai',
  scripts=['bin/saucebot'],
  packages=['saucebot'],
  install_requires=['saucenaopy']
)
