# A CherryPy site for grading CS projects
# Clay Reimann 5/13/2013
# All rights reserved

# Import CherryPy global namespace
import cherrypy
from os import path

from .modules import auth
from mako.template import Template
from mako.lookup   import TemplateLookup

# web app classes
from .modules.grade import Grade
from .modules.admin import Admin
from .modules.auth  import AuthController
from .modules.milestones import Milestones

class GradingApplication:
  """This is the main Application class."""

  def __init__(self):
    self.configPath = path.join(path.dirname(__file__), 'site.conf')
    self.lookup = TemplateLookup(directories=['/var/www/gradingsystem_us/Templates'])

    self.grades = Grade(self.lookup)

    self.admin  = Admin(self.lookup)

    self.auth   = AuthController(self.lookup)

    self.milestones = Milestones(self.lookup)

  @cherrypy.expose
  def index(self):
    u = auth.current_user()
    l = False if u is None else True
    t = self.lookup.get_template('index.html')
    r = cherrypy.request
    return t.render(_logged_in = l, _user = u, _request=r)

  @cherrypy.expose
  def default(self, *uri, **params):
    u = auth.current_user()
    l = False if u is None else True
    t = self.lookup.get_template('404.html')
    return t.render(_logged_in = l, _user = u, URI=uri, params=params)

grades = GradingApplication()
grade_app = cherrypy.Application(grades, config=grades.configPath)
grade_app.toolboxes['auth'] = auth.auth_toolbox
