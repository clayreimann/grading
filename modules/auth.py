# Based on:
#  - module: http://tools.cherrypy.org/wiki/AuthenticationAndAccessRestrictions
#  - toolbox: http://docs.cherrypy.org/stable/progguide/extending/customtools.html
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import cherrypy
from .db import auth_user

USERNAME_SESSION_KEY = '_cp_username'
USERDATA_SESSION_KEY = '_cp_userinfo'
FROMPATH_SESSION_KEY = '_cp_redirect_to'

# Create a new Toolbox.
auth_toolbox = cherrypy._cptools.Toolbox("auth")

def check_auth(*args, **kwargs):
  """
    A tool that looks in config for 'auth.restrict.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill
  """
  conditions = cherrypy.request.config.get('auth.restrict.require', None)
  if conditions is not None:
    username = cherrypy.session.get(USERNAME_SESSION_KEY, None)
    if username:
      cherrypy.request.login = username
      for condition in conditions:
        # A condition is just a callable that returns true or false
        if not condition():
          raise cherrypy.HTTPRedirect("/")
    else:
      cherrypy.session[FROMPATH_SESSION_KEY] = cherrypy.request.path_info
      raise cherrypy.HTTPRedirect("/auth/login")

auth_toolbox.restrict = cherrypy.Tool('before_handler', check_auth)

def require(*conditions):
  """
    A decorator that appends conditions to the auth.require config
    variable.
  """
  def decorate(f):
    if not hasattr(f, '_cp_config'):
      f._cp_config = dict()
    if 'auth.require' not in f._cp_config:
      f._cp_config['auth.require'] = []
    f._cp_config['auth.require'].extend(conditions)
    return f
  return decorate

# Conditions are callables that return True
# if the user fulfills the conditions they define, False otherwise
#
# They can access the current username as cherrypy.request.login
#
# Define those at will however suits the application.

def member_of(groupname):
  def check():
    # replace with actual check if <username> is in <groupname>
    return cherrypy.request.login == 'joe' and groupname == 'admin'
  return check

def name_is(reqd_username):
  return lambda: reqd_username == cherrypy.request.login


def any_of(*conditions):
  """Returns True if any of the conditions match"""
  def check():
    for c in conditions:
      if c():
        return True
    return False
  return check

# By default all conditions are required, but this might still be
# needed if you want to use it inside of an any_of(...) condition
def all_of(*conditions):
  """Returns True if all of the conditions match"""
  def check():
    for c in conditions:
      if not c():
        return False
    return True
  return check



def current_user():
  s = cherrypy.session
  u = s.get(USERDATA_SESSION_KEY, None)
  return u

# Controller to provide login and logout actions
from .base import Base

def check_credentials(username, password):
  """
    Verifies credentials for username and password.
    Returns a user dictionary on success or a None on failure
  """

  return auth_user(username, password)

class AuthController(Base):

  def __init__(self, tmpl_lookup):
    super(AuthController, self).__init__(tmpl_lookup)

  def on_login(self, user):
    """Called on successful login"""
    s = cherrypy.session
    s[USERDATA_SESSION_KEY] = user

  def on_logout(self):
    """Called on logout"""
    s = cherrypy.session
    s[USERDATA_SESSION_KEY] = None

  def get_loginform(self, username, error=None):
    return self.render("login/login.tmpl",
                        username=username,
                        error=error)


  @cherrypy.expose
  def login(self, username=None, password=None):
    if (username is None) or (password is None):
      return self.get_loginform("")

    user = check_credentials(username, password)

    if user:
      s = cherrypy.session
      from_page = s.get(FROMPATH_SESSION_KEY, None)

      # our login status changed regenerate the session
      s.regenerate()

      # this is how we know we're logged in
      s[USERNAME_SESSION_KEY] = cherrypy.request.login = username
      self.on_login(user)

      # continue on our way
      raise cherrypy.HTTPRedirect(from_page or "/")

    else:
      return self.get_loginform(username, "Username/password combination not recognized")

  @cherrypy.expose
  def logout(self):
    s = cherrypy.session
    username = s.get(USERNAME_SESSION_KEY, None)
    s[USERNAME_SESSION_KEY] = None
    from_page = s.get(FROMPATH_SESSION_KEY, None)
    if username:
      cherrypy.request.login = None
      self.on_logout()
    raise cherrypy.HTTPRedirect(from_page or "/")