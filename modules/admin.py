# Simple CherryPy site
# Clay Reimann 5/13/2013
# All rights reserved

# Import CherryPy global namespace
import cherrypy

from .base import Base
from .users import Users
from .courses import Courses

class Admin(Base):
  """
    This is where we'll hang all of the administrative tasks from.
      /users     - all of the user management stuff
      /courses   - all of the course management stuff
      /semesters - all of the assignment management stuff
  """
  def __init__(self, tmpl_lookup):
    super(Admin, self).__init__(tmpl_lookup)
    self.page_title = "Admin"
    self.users = Users(tmpl_lookup)
    self.courses = Courses(tmpl_lookup)

  @cherrypy.expose
  def index(self):
    return self.render("admin/index.html")

  @cherrypy.expose
  def assignments(self, method):
    if method == "add":
      return self.render("admin/add_assignment.html", page_title="New Assignment")
    elif method == "show":
      raise cherrypy.HTTPRedirect("/admin")
    else:
      raise cherrypy.HTTPRedirect("/admin/assignments/show")

  @cherrypy.expose
  def add(self, method, **params):
    if method == "assignment":
      return self.params_to_html(method, **params)

  def params_to_html(self, method, **params):
    html  = "<html><body style='padding:20px 30px;'><h2>"+method+"</h2><pre>"
    for p in params:
      html += p + ": " + params[p] + "\n"
    html += "</pre></body></html>"
    return html
