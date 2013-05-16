# Simple CherryPy site
# Clay Reimann 5/13/2013
# All rights reserved

# Import CherryPy global namespace
import cherrypy
import os.path

from mako.template import Template
from mako.lookup   import TemplateLookup

# web app classes
from grade.Grade import Grade
from admin.Admin import Admin

class Application:
  """This is the main Application class."""
  def __init__(self, lookup):
    self.lookup = lookup
    self.grades = Grade(self.lookup)
    self.admin  = Admin(self.lookup)

  @cherrypy.expose
  def index(self):
    t = lookup.get_template('index.html')
    return t.render(page_title="Home")

  @cherrypy.expose
  def default(self, *uri):
    return "URI: {}".format(uri)



siteConf = os.path.join(os.path.dirname(__file__), 'site.conf')
lookup = TemplateLookup(directories=['Templates'])
app = Application(lookup)

if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to Application().index().
    # siteConf is global from __init__?
    cherrypy.quickstart(app, config=siteConf)
