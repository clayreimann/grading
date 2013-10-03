# Simple CherryPy site
# Clay Reimann 5/13/2013
# All rights reserved

# Import CherryPy global namespace
import cherrypy

from .. import db
from ..base import Base
from .. import auth

class Users(Base):
  """
    The Users controller
  """
  def __init__(self, tmpl_lookup):
    super(Users, self).__init__(tmpl_lookup)
    self.page_title = "Users"

  @cherrypy.expose
  def index(self):
    """
      Lists all of the users registerd in the system
    """
    return self.render("admin/users/all.html", page_title="Users", users=db.all_users())

  @cherrypy.expose
  @auth.require(auth.has_prof_privileges())
  def add(self, **params):
    """
      Renders the form to add a user, or if params are passed
      we check to see if things are valid and if so add the
      user to the database.
    """
    errors = self.check_params(**params)
    if len(errors) == 0 and len(params) != 0:
      self.add_user(**params)
    else:
      return self.render("admin/users/add.html", page_title="New User", errors=errors, data=params)

  def check_params(self, **params):
    """
      Validates the submission before we add the user
    """
    # this will be empty if we're trying to load the page before submit
    errors = []
    if len(params) == 0:
      errors.append("")
      return errors

    if "netID" not in params or len(params["netID"]) == 0:
      errors.append("NetID is required")

    if "firstName" not in params or "lastName" not in params or \
        len(params["firstName"]) == 0 or len(params["lastName"]) == 0:
      errors.append("You must enter a full name")

    if not "pw" in params or not "pwConf" in params:
      errors.append("You must enter a password and confirmation.")
    else:
      if params["pw"] != params["pwConf"]:
        errors.append("Password and confirmation must match.")

    return errors

  def add_user(self, netID, lastName, firstName, pw, pwConf):
    """
      Adds the user to the database
    """
    db.add_user(netID, lastName, firstName, pw)
    raise cherrypy.HTTPRedirect("/admin/users/")

  @cherrypy.expose
  @auth.require(auth.has_ta_privileges())
  def show(self, user=None):
    if user == None:
      raise cherrypy.HTTPRedirect("/admin/users/")
    else:
      u = db.get_user(netID=user, recurse=True)
      return self.render("admin/users/show.html", page_title="User Management", user=u)

  @cherrypy.expose
  @auth.require(auth.has_prof_privileges())
  def remove(self, user=None, confirm=None):
    if user == None:
      return self.render("admin/users/remove.html", page_title="Remove a user", users=db.all_users())
    else:
      if confirm == None:
        u = db.get_user(user)
        return self.render("admin/users/confirm_remove.html", page_title="Confirm User Removal", user=u)
      elif confirm == "True":
        db.del_user(user)
        raise cherrypy.HTTPRedirect("/admin/users")
      else:
        return """An error has occurred in users/remove
        param: {} is of type {}""".format(confirm, type(confirm).__name__)

  @cherrypy.expose
  @auth.require(auth.has_prof_privileges())
  def bulk(self, **params):
    """
      This is a form for bulk user add
    """
    users = []
    if "users" in params:
      users = params["users"].split("\n")
    errors = self.add_users_with_errors(users)
    if len(errors) > 0 or len(params) == 0:
      return self.render("admin/users/bulk.html", page_title="Bulk User Add", errors=errors, params=params)
    else:
      raise cherrypy.HTTPRedirect("/admin/users")

  def add_users_with_errors(self, users):
    """
      add_users_with_errors adds the users passed in.  If an error is found
      with a record it is passed back out so that it can be corrected
    """
    errors = []

    for u in users:
      u = [item.strip() for item in u.split(',') if len(item.strip()) > 0]
      if len(u) == 0:
        continue

      result = ""
      if len(u) == 3:
        result = db.add_user(u[0], u[1], u[2])
      elif len(u) == 4:
        result = db.add_user(u[0], u[1], u[2], u[3])
      else:
        result = "Wrong number of fields, found {} expected 3 or 4".format(len(u))

      if result != True:
        line = "{} :: {} ".format(", ".join(u), result)
        errors.append(line)

    return errors

  @cherrypy.expose
  def passwordreset(self, **params):
    """
      passwordreset resets the user's password
    """
    errors = self.check_password_params(**params)
    if len(errors) == 0:
      self.change_password(**params)
    u = db.get_user(userID=params["ID"])
    return self.render("admin/users/show.html", page_title="User Management", user=u)

  def check_password_params(self, **params):
    """
      check_password_params ensures the passwords match
    """
    errors = []

    if "pw" not in params or "pwConf" not in params:
      errors.append("You must enter a password and confirmation")
    elif params["pw"] != params["pwConf"]:
      errors.append("Password must match Confirmation")

    return errors

  def change_password(self, ID, pw, pwConf):
    """
      change_password does changes the user's password
    """
    db.mod_user(userID=ID, password=pw)