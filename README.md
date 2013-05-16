#grading

Project for CSE 231 to grade student submissions


##Install cherrypy:
 * http://www.giantflyingsaucer.com/blog/?p=2871
 * need this patch for Python 3.3: https://bitbucket.org/cherrypy/cherrypy/commits/01b6adcb3849
 * need this patch to avoid random shutdown: https://bitbucket.org/cherrypy/cherrypy/commits/7e87ed84d9f4

##Install Mako:
  * need to edit setup.py:
    - line 1 to:
        try:
            from setuptools import setup, find_packages
        except ImportError:
            from distutils.core import setup
    - line with `find_packages` to:
        packages=['mako'],
