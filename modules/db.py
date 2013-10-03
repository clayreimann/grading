#
# A module for accessing the database
# The following functions must be provided for the site to function
#
#   CRUD (add, get, mod, del, sql=None):
#     - user
#     - course
#     - semester
#     - assignment
#     - grade
#   Autentication
#     - auth_user
#
# Changes:
#   * 08/08 CBR - created
#
# TODO:
#   * make sure all sql.execute() statements are wrapped in try/except
#   * add all_*_for_* functions where appropriate

from pymysql import connect
from pymysql import Error
from pymysql.cursors import DictCursor

from hashlib import sha256
from uuid import uuid4

def db_connect(host="localhost", db="Grading", un="grader", pw="grades", autocommit=True):
  """
    Get a connection to the database that commits our transactions as we complete them.
    The cursor returns rows as dictionaries.
  """
  con = connect(host=host, db=db, user=un, passwd=pw)
  con.autocommit(autocommit)
  return con.cursor(DictCursor)

####################
# User functions
# Users table:
# CREATE TABLE Grading.Users(
#   ID Char(36) NOT NULL, # "USR_" + uuid.uuid4()
#   NetID Char(8) NOT NULL UNIQUE,
#   LastName Varchar(32) NOT NULL,
#   FirstName Varchar(64) NOT NULL,
#   pwHash Char(64),
#   pwSalt Char(64),
#   auth_token Char(64),
#   PRIMARY KEY(ID),
#   INDEX (NetID),
#   INDEX (LastName)
# ) ENGINE=InnoDB;
####################

def hash_password(password, sql=None):
  """
    Return a tuple (pwHash, pwSalt) hashed from `password`
  """
  if password == None:
    return ("", "")

  pwSalt = sha256(str(datetime.now()).encode('utf-8')).hexdigest()
  pwHash = sha256((password + pwSalt).encode('utf-8')).hexdigest()
  return (pwHash, pwSalt)

def all_users(sql=None):
  close = False
  if sql == None:
    close = True
    sql = db_connect()
  sql.execute("SELECT * FROM Users ORDER BY NetID")
  ret = sql.fetchall()

  if close:
    sql.close()
  return ret

def add_user(netID, last_name, first_name, password=None, sql=None):
  """
    Add a new user to the database
  """
  guid = "USR_" + uuid4().hex
  pwHash, pwSalt = hash_password(password)

  cols = "ID, NetID, LastName, FirstName"
  vals = '"{}", "{}", "{}", "{}"'.format(guid, netID, last_name, first_name, pwHash, pwSalt)
  if len(pwHash) > 0:
    cols += ", pwHash, pwSalt"
    vals = '{}, "{}", "{}"'.format(vals, pwHash, pwSalt)
  query = "INSERT INTO Users ({}) VALUES({})".format(cols, vals)

  ret = False
  close = False
  if sql == None:
    close = True
    sql = db_connect()
  try:
    if sql.execute(query) == 1:
      ret = True
  except Error as e:
    ret = e

  if close:
    sql.close()

  if not ret:
    print(query)

  return ret

def get_user(userID=None, netID=None, recurse=False, sql=None):
  """
    Retrieve a user from the database
  """
  u = None

  query = "SELECT * FROM Users WHERE NetID='{}'".format(netID)
  # prefer to get users by ID
  if userID != None:
    query = "SELECT * FROM Users WHERE ID='{}'".format(userID)

  close = False
  if sql == None:
    close = True
    sql = db_connect()
  try:
    rows = sql.execute(query)
    if rows == 1:
      u = sql.fetchone()
      del u["pwHash"]
      del u["pwSalt"]
      uid = u["ID"]
      roles = []
      all_roles = get_roles_for_user(uid, sql=sql)
      for r in all_roles:
        # SemesterID, Section, UserType
        semester = get_semester(r["SemesterID"], sql=sql)
        roles.append({"Semester": semester, "Section": r["Section"], "UserType": r["UserType"]})
      u["Roles"] = roles
  except:
    pass

  return u

def mod_user(userID=None, netID=None, last_name=None, first_name=None, password=None, sql=None):
  """
    Update the user with the changed information
  """
  ret = False

  if netID == None and userID == None:
    return ret

  query = "UPDATE Users SET "

  bits = []
  if last_name:
    bits.append("LastName='{}'".format(last_name))

  if first_name:
    bits.append("FirstName='{}'".format(first_name))

  if password:
    pwHash, pwSalt = hash_password(password)
    bits.append("pwHash='{}', pwSalt='{}'".format(pwHash, pwSalt))

  query += ", ".join(bits)
  if userID:
    query += "WHERE ID='{}'".format(userID)
  else:
    query += "WHERE NetID='{}'".format(netID)

  close = False
  if sql == None:
    close = True
    sql = db_connect()

  try:
    if sql.execute(query):
      ret = True
  except Error as e:
    ret = e

  if close:
    sql.close()

  return ret

def del_user(netID, sql=None):
  """
    Deletes a user from the database
  """
  close = False
  if sql == None:
    close = True
    sql = db_connect()

  sql.execute("DELETE FROM Users WHERE NetID='{}'".format(netID))

  if close:
    sql.close()


####################
# Course functions
# Couse table:
# CREATE TABLE Grading.Courses(
#   ID Char(36), # "CRS_" + uuid.uuid4()
#   CourseNumber Char(50) UNIQUE,
#   PRIMARY KEY(ID),
#   INDEX(CourseNumber)
# ) ENGINE=InnoDB;
####################

def all_courses(sql=None):
  """
    Returns a list of all the courses
  """
  close = False
  if sql == None:
    close = True
    sql = db_connect()

  sql.execute("SELECT * FROM Courses ORDER BY CourseNumber")
  ret = sql.fetchall()

  if close:
    sql.close()

  return ret

def add_course(courseNum, sql=None):
  """
    Add a course
  """
  guid = "CRS_" + uuid4().hex
  cols = "ID, CourseNumber"
  vals = "'{}', '{}'".format(guid, str(courseNum).upper())
  query = "INSERT INTO Courses ({}) VALUES({})".format(cols, vals)

  ret = False
  close = False
  if sql == None:
    close = True
    sql = db_connect()
  try:
    ret = True if sql.execute(query) == 1 else False
  except Error as e:
    ret = False
  if close:
    sql.close()

  return ret

def get_course(guid=None, courseNumber=None, sql=None):
  """
    Returns a course record
  """
  if guid == None and courseNumber == None:
    return None

  course = None

  query = "SELECT * FROM Courses WHERE CourseNumber='{}'".format(courseNumber)
  # prefer to look up course by ID when possible
  if guid != None:
    query = "SELECT * FROM Courses WHERE ID='{}'".format(guid)

  close = False
  if sql == None:
    close = True
    sql = db_connect()
  count = sql.execute(query)

  if count == 1:
    course = sql.fetchone()
    cid = course["ID"]
    query = "SELECT * FROM Semesters WHERE CourseID='{}'".format(cid)
    sql.execute(query)
    semesters = []
    for s in sql.fetchall():
      semesters.append(s)
    course["semesters"] = semesters
  if close:
    sql.close()

  return course

def mod_course(guid, courseNum, sql=None):
  """
    Changes a course record
  """
  pass

def del_course(guid, sql=None):
  """
    Deletes a course from the database
  """
  pass


####################
# Semester functions
# Semester table:
# CREATE TABLE Grading.Semesters(
#   ID Char(38), # generated by "S_" + uuid.uuid4()
#   Name Char(4),
#   Class Char(38),
#   PRIMARY KEY(ID, Class),
#   INDEX(Class),
#   INDEX(Name),
#   FOREIGN KEY (Class)
#     REFERENCES Grading.Courses(ID)
#     ON UPDATE CASCADE
#     ON DELETE RESTRICT
# ) ENGINE=InnoDB;
####################

def all_semesters(sql=None):
  """
    Returns a list of all the semesters
    semester = {
      "ID": ID,
      "Name": Name,
      "CourseNumber": Courses.CourseNumber
    }
  """
  query = """SELECT S.ID AS ID, S.Name AS Name, C.CourseNumber AS CourseNumber
             FROM Semesters AS S INNER JOIN Courses AS C ON S.CourseID=C.ID
             ORDER BY S.Ordinal DESC"""

  close = False
  if sql == None:
    close = True
    sql = db_connect()

  sql.execute(query)
  ret = sql.fetchall()

  if close:
    sql.close()

  return ret

def add_semester(courseID, name, ordinal, sql=None):
  """
    Add a semester
    !! This should be using transactions to be safe, but we're not for now
  """
  guid = "SEM_" + uuid4().hex
  cols = "ID, CourseID, Name, Ordinal"
  vals = "'{}', '{}', '{}', '{}'".format(guid, courseID, name, ordinal)
  query = "INSERT INTO Semesters ({}) VALUES({})".format(cols, vals)

  ret = False
  close = False
  if sql == None:
    close = True
    sql = db_connect()
  try:
    if sql.execute(query) == 1:
      ret = True
  except Error as e:
    ret = e
  if close:
    sql.close()

  return ret

def get_semester(guid=None, recurse=False, sql=None):
  """
    Returns a semester record
  """
  if guid == None:
    return None

  semester = None

  query = "SELECT * FROM Semesters WHERE ID='{}'".format(guid)

  close = False
  if sql == None:
    close = True
    sql = db_connect()

  count = sql.execute(query)

  #count == 1 means it's unique (should be anyways)
  if count == 1:
    semester = sql.fetchone()
    query = "SELECT CourseNumber FROM Courses WHERE ID='{}'".format(semester["CourseID"])
    sql.execute(query)

    semester["Course"] = sql.fetchone()["CourseNumber"]

    # get categories
    if recurse:
      sid = semester["ID"]
      semester["Categories"] = get_categories_for_semester(sid, recurse=recurse, sql=sql)

  if close:
    sql.close()

  return semester

def mod_semester(guid, courseNum, sql=None):
  """
    Changes a semester record
  """
  pass

def del_semester(guid, sql=None):
  """
    Deletes a semester from the database
  """
  pass

####################
# Category functions
# Categories table:
# CREATE TABLE Grading.Categories(
#   ID Char(36),
#   CourseID Char(36),
#   Name Char(40),
#   PRIMARY KEY(ID),
#   FOREIGN KEY (CourseID)
#     REFERENCES Grading.Courses(ID)
#     ON UPDATE CASCADE
#     ON DELETE CASCADE
# ) ENGINE=InnoDB
####################
def all_categories(sql=None):
  """
    Returns a list of all the categories
  """
  close = False
  if sql == None:
    close = True
    sql = db_connect()

  sql.execute("SELECT * FROM Categories")
  ret = sql.fetchall()

  if close:
    sql.close()

  return ret

def add_category(semesterID, name, sql=None):
  """
    Add a category
  """
  guid = "CAT_" + uuid4().hex
  cols = "ID, SemesterID, Name"
  vals = "'{}', '{}', '{}'".format(guid, semesterID, name)
  query = "INSERT INTO Categories ({}) VALUES({})".format(cols, vals)

  close = False
  if sql == None:
    close = True
    sql = db_connect()

  ret = False
  try:
    result = sql.execute(query)
    if result == 1:
      ret = True
  except Error as e:
    ret = e

  if close:
    sql.close()

  return ret

def get_category(guid=None, recurse=False, sql=None):
  """
    Returns a category record
  """
  if guid == None:
    return None

  category = None

  # fallback query
  query = "SELECT * FROM Categories WHERE ID='{}'".format(guid)

  close = False
  if sql == None:
    close = True
    sql = db_connect()
  count = sql.execute(query)

  if count == 1:
    category = sql.fetchone()

    if recurse:
      cid = category["ID"]
      query = "SELECT * FROM Assignments WHERE CategoryID='{}'".format(cid)
      sql.execute(query)

      assignments = []
      for a in sql.fetchall():
        assignments.append(a)

      assignments.sort(key=lambda a: a['Name'])
      category["Assignments"] = assignments

  if close:
    sql.close()

  return category

def get_categories_for_semester(semesterID=None, recurse=False, sql=None):
  """
    get_categories_for_semester does xyz
  """
  categories = []

  if semesterID == None:
    return categories

  close = False
  if sql == None:
    close = True
    sql = db_connect()

  query = "SELECT ID FROM Categories WHERE SemesterID='{}'".format(semesterID)
  sql.execute(query)
  ids = []
  for a in sql.fetchall():
    ids.append(a["ID"])

  for i in ids:
    categories.append( get_category(i, recurse=recurse, sql=sql) )

  if close:
    sql.close()

  return categories

def mod_category(guid, courseNum, sql=None):
  """
    Changes a category record
  """
  pass

def del_category(guid, sql=None):
  """
    Deletes a category from the database
  """
  pass

####################
# Assignment functions
# Assignment table:
# CREATE TABLE Grading.Assignments(
#   ID Char(38) PRIMARY KEY, # generated by "A_" + uuid.uuid4()
#   Semester Char(38) NOT NULL,
#   Name Varchar(100) NOT NULL,
#   Parts TinyInt UNSIGNED NOT NULL,
#   Points Numeric(9,2) NOT NULL,
#   INDEX(Semester),
#   FOREIGN KEY (Semester)
#     REFERENCES Grading.Semesters(ID)
#     ON UPDATE CASCADE
#     ON DELETE RESTRICT
# ) ENGINE=InnoDB;
####################

def all_assignments(sql=None):
  """
  """
  ret = []
  return ret

def add_assignment(categoryID, name, summary, desc, points, dueDate, releaseDate, sql=None):
  """
  """
  guid = "AST_" + uuid4().hex
  cols = "ID, CategoryID, Name, Summary, Description, DueDate, ReleaseDate, Points"
  vals = "'{}', '{}', '{}', '{}', '{}', '{}', '{}', {}"
  vals = vals.format(guid, categoryID, name, summary, desc, dueDate, releaseDate, points)

  ret = False
  query = "INSERT INTO Grading.Assignments ({}) VALUES({})".format(cols, vals)

  close = False
  if sql == None:
    close = True
    sql = db_connect()

  try:
    if sql.execute(query) == 1:
      ret = True
  except Error as e:
    ret = (query, e)

  if close:
    sql.close()

  return ret

def get_assignment(guid, sql=None):
  """
  """
  pass

def mod_assignment(guid, name, semester, parts, points, sql=None):
  """
  """
  pass

def del_assignment(guid, sql=None):
  """
  """
  pass



####################
# Role functions
####################
def all_roles_for_semester(semesterID, sql=None):
  """
    all_roles_for_semester does xyz
  """
  close = False
  if sql == None:
    close = True
    sql = db_connect()

  ret = []
  query ="""SELECT U.LastName AS LastName, U.FirstName AS FirstName, U.NetID AS NetID, R.Section AS Section, R.UserType AS UserType
            FROM Roles AS R INNER JOIN Users AS U ON R.UserID=U.ID
            WHERE SemesterID='{}' ORDER BY R.UserType, R.Section, U.LastName, U.FirstName""".format(semesterID)
  try:
    sql.execute(query)
    ret = sql.fetchall()
  except Error as e:
    ret = e

  if close:
    sql.close()

  return ret


def add_role(userID, semesterID, section, utype="STUDENT", sql=None):
  """
    Add a role
  """
  guid = "ROL_" + str(uuid4())
  cols = "UserID, SemesterID, Section, UserType"
  vals = "'{}', '{}', '{}', '{}'".format(userID, semesterID, section, utype)
  query = "INSERT INTO Roles ({}) VALUES({})".format(cols, vals)

  close = False
  if sql == None:
    close = True
    sql = db_connect()

  ret = False
  try:
    ret = True if sql.execute(query) == 1 else False
  except Error as e:
    ret = False

  if close:
    sql.close()

  return ret

def get_roles_for_user(userID=None, sql=None):
  """
    Returns a role record
  """
  if userID == None:
    return None

  role = None

  # fallback query
  query = "SELECT SemesterID, Section, UserType FROM Roles WHERE UserID='{}'".format(userID)

  close = False
  if sql == None:
    close = True
    sql = db_connect()
  sql.execute(query)

  roles = sql.fetchall()
  if close:
    sql.close()

  return roles

def mod_role(userID=None, courseID=None, section=None, utype=None, sql=None):
  """
    Changes a role record
  """
  pass

def del_role(userID=None, courseID=None, sql=None):
  """
    Deletes a role from the database
  """
  pass


####################
# Security functions
####################

#
# Constants for authentication
#
ADMIN   = 3
PROF    = 2
TA      = 1
STUDENT = 0

def auth_user(netID, passwordText, sql=None):
  user = None

  close = False
  if sql == None:
    close = True
    sql = db_connect()
  cnt = sql.execute("SELECT * FROM Users WHERE NetID='{}'".format(netID))

  if cnt == 1:
    user = sql.fetchone()

    pwHash = sha256((passwordText + user["pwSalt"]).encode('utf-8')).hexdigest()
    if pwHash != user["pwHash"]:
      print('username/password combination not recognized')
      user = None
    else:
      del user["pwHash"]
      del user["pwSalt"]
      user["FullName"] = "{} {}".format(user["FirstName"], user["LastName"])

      query = "SELECT UserType, SemesterID FROM Roles WHERE UserID='{}'".format(user["ID"])
      sql.execute(query)
      roles = {}
      for r in sql.fetchall():
        sem = r["SemesterID"]
        role = r["UserType"]

        if role == "ADMIN":
          role = ADMIN
        elif role == "PROF":
          role = PROF
        elif role == "TA":
          role = TA
        else:
          role = STUDENT

        roles[sem] = role

      user["Roles"] = roles


  if close:
    sql.close()

  return user

