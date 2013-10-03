# Simple CherryPy site
# Clay Reimann 5/13/2013
# All rights reserved

# Import CherryPy global namespace
import cherrypy

from . import db
from . import auth
from .base import Base

class Projects(Base):
  """
  This is the controller for Projects
  """
  def __init__(self, lookup):
    super(Projects, self).__init__(lookup)
    self.page_title = "Projects"

  @cherrypy.expose
  def index(self):
    """
      index shows all the projects for a semester
    """
    sem = auth.current_semester()
    projs = db.get_categories_for_semester(sem)
    return self.render("projects/all.html", projects=projs)
