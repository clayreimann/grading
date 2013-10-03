# Simple CherryPy site
# Clay Reimann 5/13/2013
# All rights reserved

# Import CherryPy global namespace
import cherrypy
from .auth import current_user

class Base:
  """Define a base class for all pages"""
  def __init__(self, tmpl_lookup):
    self.tmpl_lookup = tmpl_lookup
    self.page_title = "MSU Grading System"

  def render(self, template_name, **kwargs):
    t = self.tmpl_lookup.get_template(template_name)
    kwargs["_user"] = current_user()
    kwargs["_request"] = cherrypy.request
    kwargs["_session"] = cherrypy.session
    kwargs["_active"] = cherrypy.request.path_info.split("/")[1]
    if "page_title" not in kwargs:
      kwargs["page_title"] = self.page_title
    return t.render(**kwargs)