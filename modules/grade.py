# Clay Reimann 5/13/2013
# All rights reserved

import os
import cherrypy
from .base import Base

FILES_BASE_PATH = "/var/www/sudostudios_com/user/cse231/Handin"

class Grade(Base):
  """
    This handles all of the grading parts of the site
  """

  def __init__(self, tmpl_lookup):
    super(Grade, self).__init__(tmpl_lookup)
    self.sections = sorted([s for s in os.listdir(FILES_BASE_PATH) if s[0] != '.'])

  @cherrypy.expose
  def index(self):
    return self.render('grade/grade_index.tmpl',
                      page_title="Grades",
                      sections=self.sections)

  @cherrypy.expose
  def default(self, *path):
    """
      This is where we handle routing the request
    """
    if len(path) == 1:
      return self.section(path[0])
    elif len(path) == 2:
      return self.assignments(path[0], path[1])
    elif len(path) == 3:
      return self.submission(path[0], path[1], path[2])
    return "path: {}".format(path)

  def section(self, section):
    """
      List all of the students in the section
    """
    section_path = os.path.join(FILES_BASE_PATH, section)
    students = sorted([s for s in os.listdir(section_path) if s[0] != '.'])

    return self.render('grade/section.tmpl',
                    page_title=section,
                    section=section,
                    students=students)

  def assignments(self, section, student):
    """
      List all of the assignments for a student
    """
    student_path = os.path.join(FILES_BASE_PATH, section, student)
    assignments = sorted([s for s in os.listdir(student_path) if s[0] != '.'])

    return self.render('grade/student.tmpl',
                    page_title="{}::{}".format(student, section),
                    section=section,
                    student=student,
                    assignments=assignments)

  def submission(self, section, student, assignment):
    """
      Displays a submission
    """
    submission_name = "proj{}.py".format(assignment)
    submission_path = os.path.join(FILES_BASE_PATH, section, student, assignment, submission_name)
    lines = open(submission_path).readlines()

    return self.render('grade/submission.tmpl',
                    page_title="{} {}".format(student, submission_name),
                    section=section,
                    student=student,
                    assignment=assignment,
                    script=''.join(lines))

  @cherrypy.expose
  def results(self, section, student, assignment):
    """
      Runs a script and returns the result
    """
    return "{}".format("Not running script yet")

