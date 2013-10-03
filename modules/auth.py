# Based on:
#  - module: http://tools.cherrypy.org/wiki/AuthenticationAndAccessRestrictions
#  - toolbox: http://docs.cherrypy.org/stable/progguide/extending/customtools.html
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import cherrypy
from . import db

USERNAME_SESSION_KEY = '_cp_username'
USERDATA_SESSION_KEY = '_cp_userinfo'
CUR_CRS_SESSION_KEY  = '_cp_current_course'
FROMPATH_SESSION_KEY = '_cp_redirect_to'

# Create a new Toolbox.
auth_toolbox = cherrypy._cptools.Toolbox("auth")

def current_user():
  return cherrypy.session.get(USERDATA_SESSION_KEY, None)

def current_semester():
  return cherrypy.session.get(CUR_CRS_SESSION_KEY, None)


def check_auth(*args, **kwargs):
  """
    A tool that looks in config for 'auth.restrict.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill
  """
  r = cherrypy.request
  s = cherrypy.session

  username = s.get(USERNAME_SESSION_KEY, None)
  course = s.get(CUR_CRS_SESSION_KEY, None)
  # require a course to be selected
  if username and not course and r.path_info != '/auth/course':
    raise cherrypy.HTTPRedirect("/auth/course")

  conditions = r.config.get('auth.restrict.require', None)
  if conditions is not None:
    if username:
      r.login = username
      for condition in conditions:
        # A condition is just a callable that returns true or false
        if not condition():
          raise cherrypy.HTTPRedirect("/auth/not-authorized")
    else:
      s[FROMPATH_SESSION_KEY] = r.path_info
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
    if 'auth.restrict' not in f._cp_config:
      f._cp_config['auth.restrict.on'] = True
    if 'auth.restrict.require' not in f._cp_config:
      f._cp_config['auth.restrict.require'] = []
    f._cp_config['auth.restrict.require'].extend(conditions)
    return f
  return decorate

# Conditions are callables that return True
# if the user fulfills the conditions they define, False otherwise
# Define those at will however suits the application.

def has_admin_privileges():
  def check():
    sem = current_semester()
    usr = current_user()
    if sem == None or sem not in usr["Roles"]:
      return False
    return usr["Roles"][current_semester()] >= db.ADMIN
  return check

def has_prof_privileges():
  def check():
    sem = current_semester()
    usr = current_user()
    if sem == None or sem not in usr["Roles"]:
      return False
    return usr["Roles"][current_semester()] >= db.PROF
  return check

def has_ta_privileges():
  def check():
    sem = current_semester()
    usr = current_user()
    if sem == None or sem not in usr["Roles"]:
      return False
    return usr["Roles"][current_semester()] >= db.TA
  return check

def has_student_privileges():
  def check():
    sem = current_semester()
    usr = current_user()
    if sem == None or sem not in usr["Roles"]:
      return False
    return usr["Roles"][current_semester()] >= db.STUDENT
  return check


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


# Controller to provide login and logout actions
from .base import Base

def check_credentials(username, password):
  """
    Verifies credentials for username and password.
    Returns a user dictionary on success or a None on failure
  """

  return db.auth_user(username, password)


ROLES_MAP = {
  db.ADMIN: 'Admin',
  db.PROF: 'Prof',
  db.TA: 'TA',
  db.STUDENT: 'Student'
}

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


  @cherrypy.expose
  def login(self, username=None, password=None):
    if (username is None) or (password is None):
      return self.render("login/login.html",
                        page_title="Login",
                        username=username,
                        errors=[])

    user = check_credentials(username, password)

    if user:
      s = cherrypy.session
      from_page = s.get(FROMPATH_SESSION_KEY, None)

      # our login status changed regenerate the session
      s.regenerate()

      # this is how we know we're logged in
      s[USERNAME_SESSION_KEY] = cherrypy.request.login = username
      s[FROMPATH_SESSION_KEY] = from_page
      self.on_login(user)

      # continue on our way
      raise cherrypy.HTTPRedirect("/auth/course")

    else:
      return self.render("login/login.html",
                        page_title="Login",
                        username=username,
                        errors=["User name / Password combination not recognized"])

  @cherrypy.expose
  @require() # empty to require a valid login
  def course(self, sem=None):
    """
      semester_select does xyz
    """
    errors = []
    if sem != None:
      sem = db.get_semester(guid=sem)
      if sem != None:
        s = cherrypy.session
        s[CUR_CRS_SESSION_KEY] = sem["ID"]

        from_page = s.get(FROMPATH_SESSION_KEY, None)
        s[FROMPATH_SESSION_KEY] = None

        raise cherrypy.HTTPRedirect(from_page or "/profile")

      else:
        errors.append("<h3>Semester not found</h3>. If you believe you are seeing this message in error please contact your professor.")

    u = current_user()
    roles = {}
    for r in u['Roles']:
      roles[r] = db.get_semester(guid=r)
      roles[r]['Type'] = ROLES_MAP[u['Roles'][r]]
    return self.render("login/courses.html", _navigation=False, page_title="Select a Course", roles=roles)

  @cherrypy.expose
  def not_authorized(self):
    """
      not_authorized does xyz
    """
    return self.render("login/no-auth.html", page_title="Insufficient Permissions")

  @cherrypy.expose
  def logout(self):
    s = cherrypy.session
    username = s.get(USERNAME_SESSION_KEY, None)
    s[USERNAME_SESSION_KEY] = None
    if username:
      cherrypy.request.login = None
      self.on_logout()
    raise cherrypy.HTTPRedirect("/")