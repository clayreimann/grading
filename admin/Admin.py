# Simple CherryPy site
# Clay Reimann 5/13/2013
# All rights reserved

# Import CherryPy global namespace
import cherrypy

from mako.template import Template
from mako.lookup   import TemplateLookup

class Admin:
  """Administrative tasks here"""
  def __init__(self, tmpl_lookup):
    self.tmpl_lookup = tmpl_lookup

  @cherrypy.expose
  def index(self):
    t = self.tmpl_lookup.get_template("admin/index.html")
    return t.render(page_title="Admin")
