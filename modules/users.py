# Simple CherryPy site
# Clay Reimann 5/13/2013
# All rights reserved

# Import CherryPy global namespace
import cherrypy

from . import db
from .base import Base

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
  def add(self, **params):
    """
      Renders the form to add a user, or if params are passed
      we check to see if things are valid and if so add the
      user to the database.
    """
    error = self.check_params(**params)
    if error == None and len(params) != 0:
      self.add_user(**params)
    else:
      return self.render("admin/users/add.html", page_title="New User", error=error, data=params)

  def check_params(self, **params):
    """
      Validates the submission before we add the user
    """
    # this will be empty if we're trying to load the page before submit
    if len(params) == 0:
      return ""

    if (not "pw" in params) or (not "pwConf" in params):
      return "You must enter a password and confirmation."
    if params["pw"] != params["pwConf"]:
      return "Password and confirmation do not match."
    if len(params["netID"]) == 0 or len(params["firstName"]) == 0 or len(params["lastName"]) == 0:
      return "NetID, first name, and last name are required fields."

    return None

  def add_user(self, netID, lastName, firstName, pw, pwConf):
    """
      Adds the user to the database
    """
    db.add_user(netID, lastName, firstName, pw)
    raise cherrypy.HTTPRedirect("/admin/users/")

  @cherrypy.expose
  def show(self, user=None):
    if user == None:
      raise cherrypy.HTTPRedirect("/admin/users/")
    else:
      u = db.get_user(user)
      return self.render("admin/users/show.html", page_title="User Management", user=u)

  @cherrypy.expose
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