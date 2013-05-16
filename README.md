#CSE 231 Grading Server

Project for the [CSE 231 class](http://www.cse.msu.edu/~cse231) at Michigan State University to grade student 
submissions.  Currently very, very alpha.  This project is built with CherryPy 3.2 (with some additional patches)
as well as Mako 0.8.0


##Install cherrypy:
 * http://www.giantflyingsaucer.com/blog/?p=2871
 * need this patch for Python 3.3: https://bitbucket.org/cherrypy/cherrypy/commits/01b6adcb3849
 * need this patch to avoid random shutdown: https://bitbucket.org/cherrypy/cherrypy/commits/7e87ed84d9f4

##Install Mako:
  * need to edit setup.py:
    - line with `find_packages` to:
        `packages=['mako'],`
    - line 1 to:

```python
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
```
