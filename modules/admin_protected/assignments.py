# Simple CherryPy site
# Clay Reimann 5/13/2013
# All rights reserved

# Import CherryPy global namespace
import cherrypy
from datetime import datetime

from .. import db
from ..base import Base

# a translation map which maps ' ' -> None
TRANS_MAP = str.maketrans("", "", " ")

class Assignments(Base):
  """
    The assignments controller
  """
  def __init__(self, tmpl_lookup):
    super(Assignments, self).__init__(tmpl_lookup)
    self.page_title = "Assignments"

  @cherrypy.expose
  def index(self):
    """
      Displays all of the assignments in the system
    """
    return self.render("admin/assignments/all.html", assignments=db.all_assignments())

  @cherrypy.expose
  def add(self, **params):
    """
      Renders the form to add a assignment, or if params
      are passed then we validate and add the assignment.
    """
    errors = self.check_params(**params)
    if len(errors) == 0 and len(params) > 0:
      errors = self.add_assignment(**params)

    return self.render("admin/assignments/add.html",
      errors=errors,
      params=params,
      semesters=db.all_semesters(),
      categories=db.all_categories())

  def check_params(self, **params):
    """
      Checks the params and returns a description of the
      error, or None
    """
    errs = []

    if len(params) == 0:
      return errs

    if len(params) == 2 and "crs" in params and "cat" in params:
      return errs

    if "name" not in params or len(params["name"]) == 0:
      errs.append("A label for the assignment is required.")
    else:
      if len(params["name"]) > 100:
        errs.append("Your name for this assignment is too long")

    if "cat" not in params or len(params["cat"]) == 0:
      errs.append("You must associate this assignment with a category")
    if "sem" not in params or len(params["sem"]) == 0:
      errs.append("You must associate this assignment with a semester")

    if "summary" not in params or len(params["summary"]) == 0:
      errs.append("You must provide a summary for the assignment")

    if "due" not in params or len(params["due"]) != 16:
      errs.append("You must provide a valid due date")

    if "release" in params:
      if len(params["release"]) != 16 and len(params["release"]) > 0:
        errs.append("You must provide a valid release date")

    if "points" not in params or len(params["points"]) == 0:
      try:
        float(params["points"])
      except Exception as e:
        errs.append(str(e))

    return errs

  def add_assignment(self, sem, cat, name, summary, description, points, due, release):
    """
      Call the database function to add a course
    """
    if len(release) == 0:
      release = str(datetime.now())[:16]
    success_or_error = db.add_assignment(cat, name, summary, description, points, due, release)
    if success_or_error == True:
      raise cherrypy.HTTPRedirect("/admin/semesters/show/"+sem)
    else:
      return [str(success_or_error)]

  @cherrypy.expose
  def show(self, assignment=None, **params):
    """
      Displays one assignment's listing
    """
    # if assignment == None:
    raise cherrypy.HTTPRedirect("/admin/assignments")
    # else:
    #   s = db.get_assignment(guid=assignment, recurse=True)
    #   return self.render("admin/assignments/show.html", assignment=s, errors=errors)

  @cherrypy.expose
  def remove(self, assignment=None):
    """
      Displays a list of the assignments in the system for removal
    """
    # return self.render("admin/assignments/remove.html")
