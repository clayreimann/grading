
# Simple CherryPy site
# Clay Reimann 5/13/2013
# All rights reserved

# Import CherryPy global namespace
import cherrypy

import re

from .. import db
from ..base import Base

dict_match = re.compile(r"^(\w+)\[(\w+)\]")

class Roles(Base):
  """
    The Roles controller
  """
  def __init__(self, tmpl_lookup):
    super(Roles, self).__init__(tmpl_lookup)
    self.page_title = "Roles"

  @cherrypy.expose
  def index(self):
    """
      Lists all of the users registerd in the system
    """
    return self.render("admin/roles/all.html", page_title="Class Assignment",
                        semesters=db.all_semesters())

  @cherrypy.expose
  def show(self, semester=None):
    """
      Shows all of the roles for a given semester
    """
    if semester == None:
      raise cherrypy.HTTPRedirect("/admin/roles")
    else:
      return self.render("admin/roles/show.html", page_title="Semester Roles",
                          roles=db.all_roles_for_semester(semester))

  @cherrypy.expose
  def single(self, **params):
    """
      single adds a single user role
    """
    errors = []
    if len(params) != 0:
      if "user" not in params or len(params["user"]) == 0:
        errors.append("You must specify a user")
      if "role" not in params or len(params["role"]) == 0:
        errors.append("You must specify a role")
      if "semester" not in params or len(params["semester"]) == 0:
        errors.append("You must specify a course for the role")
      if "section" in params:
        if len(params["section"]) > 4:
          errors.append("Section must be 4 characters or less")

      if len(errors) == 0:
        section = "000"
        if "section" in params and len(params["section"]) > 0:
          section = params["section"]
        result = db.add_role(params["user"], params["semester"], section, params["role"])
        if result == True:
          raise cherrypy.HTTPRedirect("/admin/roles")
        else:
          errors.append(str(result))
    return self.render("admin/roles/single.html", page_title="Assign User",
      users=db.all_users(), semesters=db.all_semesters(), params=params, errors=errors)

  @cherrypy.expose
  def add(self, **params):
    """
      Renders a form grid so roles can be set for multiple users
      at the same time.
    """
    params = self.parse_dicts(**params)
    errors = self.add_roles_with_errors(**params)
    if len(errors) == 0 and len(params) != 0:
      raise cherrypy.HTTPRedirect("/admin/roles")
    else:
      users = db.all_users()
      semesters = db.all_semesters()
      return self.render("admin/roles/add.html", page_title="New User",
                users=users, semesters=semesters, errors=errors)

  def parse_dicts(self, **params):
    """
      parse_dicts converts the string parameters into dictionaries
      so foo['bar'] and foo['baz'] will be in the same parameters
      a lá PHP or Rails style forms
    """
    new_params = {}
    for p in params:
      m = dict_match.match(p)
      if m != None:
        name, key = m.group(1, 2)
        if len(params[p]) > 0:
          if name in new_params:
            new_params[name][key] = params[p]
          else:
            new_params[name] = {key: params[p]}
      else:
        new_params[p] = params[p]

    return new_params

  def add_roles_with_errors(self, **params):
    """
      Validates the submission before we add users to a class
    """
    errors = []
    if len(params) == 0:
      errors.append('')
      return errors

    for uid in params:
      user = params[uid]
      if "Course" not in user:
        errors.append( (uid, user) )
        continue

      if "Role" not in user:
        errors.append( (uid, user) )
        continue

      section = user["Section"] if ("Section" in user and len(user["Section"]) > 0) else "000"
      result = db.add_role(uid, user["Course"], section, user["Role"])
      if result != True:
        errors.append( (u, user) )

    return errors

  @cherrypy.expose
  def remove(self, user=None, confirm=None):
    return ""