# Simple CherryPy site
# Clay Reimann 5/13/2013
# All rights reserved

# Import CherryPy global namespace
import cherrypy

from .. import db
from ..base import Base

# a translation map which maps ' ' -> None
TRANS_MAP = str.maketrans("", "", " ")

class Semesters(Base):
  """
    The semesters controller
  """
  def __init__(self, tmpl_lookup):
    super(Semesters, self).__init__(tmpl_lookup)
    self.page_title = "Semesters"

  @cherrypy.expose
  def index(self):
    """
      Displays all of the semesters in the system
    """
    return self.render("admin/semesters/all.html", semesters=db.all_semesters())

  @cherrypy.expose
  def add(self, **params):
    """
      Renders the form to add a semester, or if params
      are passed then we validate and add the semester.
    """
    errors = self.check_params(**params)
    if len(errors) == 0 and len(params) > 0:
      errors = self.add_semester(**params)

    return self.render("admin/semesters/add.html",
      errors=errors,
      params=params,
      courses=db.all_courses())

  def check_params(self, **params):
    """
      Checks the params and returns a description of the
      error, or None
    """
    errs = []

    if len(params) == 0:
      params["proj"] = []
      return errs

    if "name" not in params or len(params["name"]) == 0:
      errs.append("A label for the semester is required.")
    else:
      if len(params["name"]) > 9:
        errs.append("Your name for this semester is too long")

    if "course" not in params or len(params["course"]) == 0:
      errs.append("You must associate this semester with a course")

    # params["proj"] = [p.translate(TRANS_MAP) for p in params["proj"] if len(p.translate(TRANS_MAP)) > 0]
    # if "proj" not in params or len(params["proj"]) == 0:
    #   errs.append("You must have assignments in this semester")

    return errs

  def add_semester(self, course, name, crs_ord):
    """
      Call the database function to add a course
    """
    # proj = [p.translate(TRANS_MAP) for p in proj if len(p.translate(TRANS_MAP)) > 0]
    success_or_error = db.add_semester(course, name, crs_ord)
    if success_or_error == True:
      raise cherrypy.HTTPRedirect("/admin/semesters")
    else:
      return [str(success_or_error)]

  @cherrypy.expose
  def show(self, semester=None, **params):
    """
      Displays one semester's listing
    """
    if semester == None:
      raise cherrypy.HTTPRedirect("/admin/semesters")
    else:
      errors = []
      if "cat_name" in params and len("cat_name") > 0:
        res = db.add_category(semester, params["cat_name"])
        if res != True:
          errors.append(str(res))
      s = db.get_semester(guid=semester, recurse=True)
      title = "{} | {}".format(s["Course"], s["Name"])
      return self.render("admin/semesters/show.html", page_title=title, semester=s, errors=errors)

  @cherrypy.expose
  def remove(self, semester=None):
    """
      Displays a list of the semesters in the system for removal
    """
    return self.render("admin/semesters/remove.html")
