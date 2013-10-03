
Install cherrypy:
 * http://www.giantflyingsaucer.com/blog/?p=2871

 Install Mako:
  * need to edit setup.py:
    - line 1 to:
        try:
            from setuptools import setup, find_packages
        except ImportError:
            from distutils.core import setup
    - line with `find_packages` to:
        packages=['mako'],
