DROP DATABASE IF EXISTS Grading;

CREATE DATABASE Grading
  DEFAULT CHARACTER SET utf8
  DEFAULT COLLATE utf8_general_ci;

CREATE USER 'grader'@'localhost' IDENTIFIED BY 'grades';

GRANT ALTER, CREATE, DELETE, DROP, INDEX, INSERT, SELECT, UPDATE
  ON Grading.*
  TO 'grader'@'localhost';

CREATE TABLE Grading.Users(
  ID Char(36) NOT NULL, # "USR_" + uuid.uuid4()
  NetID Char(8) NOT NULL UNIQUE,
  LastName Varchar(32) NOT NULL,
  FirstName Varchar(64) NOT NULL,
  pwHash Char(64),
  pwSalt Char(64),
  auth_token Char(64),
  PRIMARY KEY(ID),
  INDEX (NetID),
  INDEX (LastName)
) ENGINE=InnoDB;

CREATE TABLE Grading.Courses(
  ID Char(36), # "CRS_" + uuid.uuid4()
  CourseNumber Char(50) UNIQUE,
  PRIMARY KEY(ID),
  INDEX(CourseNumber)
) ENGINE=InnoDB;

CREATE TABLE Grading.Semesters(
  ID Char(36), # "SEM_" + uuid.uuid4()
  CategoryID Char(36),
  Name Char(9),
  Ordinal TinyInt UNSIGNED,
  PRIMARY KEY(ID, CategoryID),
  INDEX(CategoryID),
  INDEX(Name),
  FOREIGN KEY (CategoryID)
    REFERENCES Grading.Categories(ID)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Grading.Roles(
  ID Char(36), # "ROL_" + uuid.uuid4()
  UserID Char(36) NOT NULL,
  SemesterID Char(36) NOT NULL,
  Section Char(4),
  UserType Enum("ADMIN", "PROF", "TA", "STUDENT") NOT NULL,
  PRIMARY KEY(ID),
  UNIQUE(UserID, SemesterID),
  FOREIGN KEY (UserID)
    REFERENCES Grading.Users(ID)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  FOREIGN KEY (SemesterID)
    REFERENCES Grading.Semesters(ID)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Grading.Categories(
  ID Char(36), # "CAT_" + uuid.uuid4()
  SemesterID Char(36),
  Name Char(40),
  PRIMARY KEY(ID),
  FOREIGN KEY (SemesterID)
    REFERENCES Grading.Semesters(ID)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Grading.Assignments(
  ID Char(36) PRIMARY KEY, # "AST_" + uuid.uuid4()
  CategoryID Char(36) NOT NULL,
  Name Varchar(100) NOT NULL,
  Summary Text,
  Description Text,
  DueDate Timestamp DEFAULT 0,
  ReleaseDate Timestamp DEFAULT 0,
  Points Numeric(9,2),
  INDEX(CategoryID),
  FOREIGN KEY (CategoryID)
    REFERENCES Grading.Categories(ID)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Grading.AssignmentParts(
  ID Char(36) PRIMARY KEY, # "APT_" + uuid.uuid4()
  AssignmentID Char(36) NOT NULL,
  Title TinyText NOT NULL,
  Points Numeric(9,2),
  FOREIGN KEY (AssignmentID)
    REFERENCES Grading.Assignments(ID)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB;

# we need after update and after insert triggers on Grading.SubmissionParts
# that call out to a stored procedure to re-calc the points column
CREATE TABLE Grading.Submissions(
  ID Char(36) PRIMARY KEY, # "SUB_" + uuid.uuid4()
  AssignmentID Char(36),
  OnDate Timestamp,
  Notes TinyText,
  Points Numeric(9,2),
  FOREIGN KEY (AssignmentID)
    REFERENCES Grading.Assignments(ID)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Grading.SubmissionParts(
  ID Char(36) PRIMARY KEY, # "SPT_" + uuid.uuid4()
  SubmissionID Char(36),
  PartID Char(36),
  Points Numeric(9,2)
  Comment TinyText,
  FOREIGN KEY (SubmissionID)
    REFERENCES Grading.Submissions(ID)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  FOREIGN KEY (PartID)
    REFERENCES Grading.AssignmentParts(ID)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB;