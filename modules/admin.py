# Simple CherryPy site
# Clay Reimann 5/13/2013
# All rights reserved

# Import CherryPy global namespace
import cherrypy

from . import auth

from .base import Base
from .admin_protected.users import Users
from .admin_protected.roles import Roles
from .admin_protected.courses import Courses
from .admin_protected.semesters import Semesters
from .admin_protected.assignments import Assignments

class Admin(Base):
  """
    This is where we'll hang all of the administrative tasks from.
      /users     - all of the user management stuff
      /courses   - all of the course management stuff
      /semesters - all of the assignment management stuff
  """
  _cp_config = {
    'auth.restrict.require': [auth.has_admin_privileges()]
  }

  def __init__(self, tmpl_lookup):
    super(Admin, self).__init__(tmpl_lookup)
    self.page_title = "Admin"
    self.roles = Roles(tmpl_lookup)
    self.users = Users(tmpl_lookup)
    self.courses = Courses(tmpl_lookup)
    self.semesters = Semesters(tmpl_lookup)
    self.assignments = Assignments(tmpl_lookup)

  @cherrypy.expose
  def index(self):
    return self.render("admin/index.html")

  @cherrypy.expose
  def form(self, **params):
    """
      A playground for experimenting with forms
    """
    params = self.roles.parse_dicts(**params)
    return self.render("admin/form.html", params=params);

  def params_to_html(self, method, **params):
    html  = "<html><body style='padding:20px 30px;'><h2>"+method+"</h2><pre>"
    for p in params:
      html += p + ": " + params[p] + "\n"
    html += "</pre></body></html>"
    return html
