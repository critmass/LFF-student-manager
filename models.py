"""SQLAlchemy models for LFF student manager."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    # this was lifted from the wabbler project
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    first_name = db.Column(
        db.Text,
        nullable=False
    )

    last_name = db.Column(
        db.Text,
        nullable=False
    )

    email = db.Column(
        db.Text,
        nullable=False
    )

    phone = db.Column(
        db.Text,
        nullable=False
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    # both class methods were borrowed and modified from the warbler project
    @classmethod
    def signup(cls, first_name, last_name, username, password, email, phone):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password=hashed_pwd

        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Course(db.Model):
    """Courses"""

    __tablename__= 'courses'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    title = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )


class TeachingAssistant(db.Model):
    """Assigns a TA to a course"""

    __tablename__= 'teaching_assistants'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    user = db.relationship(
        "User",
        backref = 'teach_assisting'
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey('courses.id', ondelete='CASCADE'),
        nullable=False
    )

    course = db.relationship(
        "Course",
        primaryjoin = (course_id == Course.id),
        backref = "teaching_assistants"
    )


class Secretary(db.Model):
    """Secretaries set students and TAs"""

    __tablename__ = 'secretaries'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    user = db.relationship(
        "User",
        backref = 'secretarying'
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey('courses.id', ondelete='CASCADE'),
        nullable=True
    )

    course = db.relationship(
        "Course",
        backref = 'secretaries'
    )


class Enrollment(db.Model):
    """"Student enrolled in a class in the system"""

    __tablename__= 'enrollments'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    user = db.relationship(
        "User",
        backref = 'enrollments'
    )

    teaching_assistant_id = db.Column(
        db.Integer,
        db.ForeignKey('teaching_assistants.id'),
        nullable=True
    )

    teaching_assistant = db.relationship(
        "TeachingAssistant",
        backref="students"
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey('courses.id', ondelete='CASCADE'),
        nullable=False
    )

    course = db.relationship(
        "Course",
        backref='students_enrolled'
    )


class Interaction(db.Model):

    __tablename__="interactions"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    # this is the person who had the interaction
    poster_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    poster = db.relationship(
        'User',
        primaryjoin=(User.id==poster_id),
        backref='interations_made'
        )

    # this is the student that the interaction was with
    enrollment_id = db.Column(
        db.Integer,
        db.ForeignKey('enrollments.id'),
        nullable=False
    )

    enrollment = db.relationship(
        "Enrollment",
        backref="interactions"
    )

    time_stamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )

    content = db.Column(
        db.Text,
        nullable=False
    )


class Lesson(db.Model):
    """Lessons"""

    __tablename__='lessons'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey('courses.id', ondelete='CASCADE'),
        nullable=False
    )

    course = db.relationship(
        "Course",
        backref='lessons'
    )

    title = db.Column(
        db.Text,
        nullable=False
    )

    num = db.Column(
        db.Integer,
        nullable=False
    )

    date_assigned = db.Column(
        db.Date,
        nullable=True
    )

    date_due = db.Column(
        db.Date,
        nullable=True
    )


class Assignment(db.Model):

    __tablename__='assignments'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    student_enrollment_id = db.Column(
        db.Integer,
        db.ForeignKey('enrollments.id', ondelete="CASCADE"),
        primary_key=True
    )

    student = db.relationship(
        "Enrollment",
        backref="assignments"
    )

    lesson_id = db.Column(
        db.Integer,
        db.ForeignKey('lessons.id', ondelete="CASCADE"),
        primary_key=True
    )

    lesson_info = db.relationship(
        'Lesson'
    )

    complete = db.Column(
        db.Boolean,
        nullable=False
    )

    turned_in = db.Column(
        db.Boolean,
        nullable=False
    )

    grade = db.Column(
        db.Float,
        nullable=True
    )


class BibleVerse(db.Model):
    """This is for holding popular verses to cycle through"""

    __tablename__ = "bible_verses"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    book = db.Column(
        db.Text,
        nullable=False
    )

    chapter = db.Column(
        db.Integer,
        nullable=False
    )

    verse = db.Column(
        db.Integer,
        nullable=False
    )

    #if more than verse, show the verses in between, including the bounding verses
    end_verse = db.Column(
        db.Integer,
        nullable=True
    )
