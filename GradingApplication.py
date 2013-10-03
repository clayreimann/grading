# A CherryPy site for grading CS projects
# Clay Reimann 5/13/2013
# All rights reserved

# Import CherryPy global namespace
import cherrypy
from os import path

from .modules import auth
from mako.lookup   import TemplateLookup

# web app classes
from .modules.base import Base
from .modules.grade import Grade
from .modules.admin import Admin
from .modules.auth  import AuthController
# from .modules.milestones import Milestones

class GradingApplication(Base):
  """This is the main Application class."""

  def __init__(self, base, tmpl_lookup):
    super(GradingApplication, self).__init__(tmpl_lookup)
    self.configPath = path.join(base, 'site.conf')

    self.grades = Grade(self.tmpl_lookup)
    self.admin  = Admin(self.tmpl_lookup)
    self.auth   = AuthController(self.tmpl_lookup)


  @cherrypy.expose
  def index(self):
    return self.render('index.html', page_title="Home",
                    _user=auth.current_user(),
                    _request=cherrypy.request,
                    _session=cherrypy.session)

  @cherrypy.expose
  def request(self, *uri, **params):
    return self.render('request.html', page_title="Request",
                    _user=auth.current_user(),
                    _request=cherrypy.request,
                    _session=cherrypy.session,
                    uri=uri, params=params)

  @cherrypy.expose
  def profile(self):
    """
      profile shows the user's profile
    """
    return self.render('profile.html', page_title="My Profile",
                    _user=auth.current_user(),
                    _request=cherrypy.request,
                    _session=cherrypy.session)

  @cherrypy.expose
  def default(self, *uri, **params):
    return self.render('404.html', page_title="Page Not Found",
                    _user=auth.current_user(),
                    _request=cherrypy.request,
                    _session=cherrypy.session,
                    URI=uri, params=params)


base = path.dirname(__file__)
tl = TemplateLookup(directories=[path.join(base, 'Templates')])
grades = GradingApplication(base, tl)
grade_app = cherrypy.Application(grades, config=grades.configPath)
grade_app.toolboxes['auth'] = auth.auth_toolbox
