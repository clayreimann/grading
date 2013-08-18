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
    self.page_title = "Default Page Title"

  def render(self, template_name, **kwargs):
    t = self.tmpl_lookup.get_template(template_name)
    u = current_user()
    kwargs["_logged_in"] = False
    if "page_title" not in kwargs:
      kwargs["page_title"] = self.page_title
    if u:
      kwargs["_logged_in"] = True
      kwargs["_user"] = u
    return t.render(**kwargs)

  # @cherrypy.expose
  # def default(self, *URI, **params):
  #   return self.render("404.html", URI=URI, params=params)
