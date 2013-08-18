# Milestone tracking for development
# Clay Reimann 5/22/13
# All rights reserved

import cherrypy

from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId
from datetime import datetime

from .auth import require
from .base import Base

class Milestones(Base):
  """
    This class is responsible for displaying
    all of the milestones for site development
  """

  def __init__(self, tmpl_lookup):
    super(Milestones, self).__init__(tmpl_lookup)
    self.db = MongoClient().grades.dev.milestones

  @cherrypy.expose
  def index(self, *path, **params):
    if "milestoneTitle" in params:
      p = params["parentId"] if "parentId" in params else None
      self.do_add(params["milestoneTitle"], p)
    return self.render("milestones/show.tmpl",
                        milestones = self.get_tree(),
                        path = path,
                        params = params)

  @cherrypy.expose
  def add(self, milestoneTitle, parentId, **extras):
    self.do_add(milestoneTitle, parentId)
    return self.render_tree()

  @cherrypy.expose
  def delete(self, milestoneId, **extras):
    self.do_delete(milestoneId)
    return self.render_tree()

  def render_tree(self):
    """
      Helper method to redner the milestone tree
    """
    return self.render("milestones/_tree.tmpl",
                        milestones = self.get_tree())
  def do_add(self, milestoneTitle, parentId):
    """
      Adds a milestone
    """
    r = {
          "title": milestoneTitle,
          "parent": parentId,
          "complete": False,
          "children": [],
          "created": datetime.now(),
          "deleted": False
        }

    if not parentId:
      r["parent"] = None

    r = self.db.milestones.save(r)

    if parentId:
      p = self.db.milestones.find_one({"_id": ObjectId(parentId)})
      p['children'].append(r)
      self.db.milestones.save(p)

  def do_delete(self, milestoneId):
    """
      Recursively deletes a milestone and all it's children
    """
    m = self.db.milestones.find_one(ObjectId(milestoneId))
    if m['parent']:
      p = self.db.milestones.find_one(ObjectId(m['parent']))
      p['children'].remove(m['_id'])
      self.db.milestones.save(p)

    for child in m['children']:
      self.do_delete(child)

    self.db.milestones.remove(m)

  def get_tree(self):
    tree = []
    for m in self.db.milestones.find({"parent": None}, sort=[("created", ASCENDING)]):
      tree.append(m)
    for m in tree:
      if len(m['children']) > 0:
        for i in range(len(m['children'])):
          m['children'][i] = self.get_child(m['children'][i])
    return tree

  def get_child(self, childId):
    child = self.db.milestones.find_one({"_id": ObjectId(childId)})
    if child and len(child['children']) > 0:
      for i in range(len(child['children'])):
        child['children'][i] = self.get_child(child['children'][i])
    return child





