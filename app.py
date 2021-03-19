import os
import requests as request_api

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from random import randrange

from forms import UserAddForm, LoginForm, InteractionsForm
from models import\
     db, connect_db, Interaction, User, Enrollment, BibleVerse,\
          TeachingAssistant, Course, Assignment, Lesson


CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', \
        'postgres://postgres:MTasXgD9@localhost/LFF_student_manager')
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

##############################################################################
# User signup/login/logout
# pulled from warbler project

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global.
    Either way, add a bible verse"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

    bible_verses = BibleVerse.query.all()
    bible = bible_verses[ randrange(0, len(bible_verses)) ]


    if bible.end_verse and bible.end_verse > bible.verse:
        bible_verse = request_api.get(
            f"http://bible-api.com/{bible.book}+{bible.chapter}:{bible.verse}-{bible.end_verse}"
            ).json()

    else:
        bible_verse = request_api.get(
            f"http://bible-api.com/{bible.book}+{bible.chapter}:{bible.verse}"
            ).json()

    g.bible_verse = (f"{bible_verse['text']}", f"-{bible_verse['reference']}")


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username = form.username.data,
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                email = form.email.data,
                phone = form.phone.data,
                password = form.password.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('sign_up.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('sign_up.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('log_in.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You are logged out, thanks for visiting!", 'info')

    return redirect("/login")

##############################################################################
# General user routes:


@app.route('/add_interaction/<enrollmentID>', methods=['POST'])
def add_interaction(enrollmentID):
    """Add an interaction"""

    form = request.form

    interaction = Interaction(
        poster_id = g.user.id,
        enrollment_id = enrollmentID,
        content = form.get('text'),
        time_stamp = datetime.now()
    )

    db.session.add( interaction )
    db.session.commit()

    return redirect(f"/student_page/{ enrollmentID }")


@app.route('/add_course/<courseID>' )
def add_course(courseID):

    course = Course.query.get_or_404( courseID )

    if not (course in g.user.courses_enrolled_in):

        enroll = Enrollment(
            student_id = g.user.id,
            course_id = courseID
        )

        db.session.add( enroll )
        db.session.commit()

        flash(f"Successfully enrolled in { course.title }")
    
    else:
        flash(f"Failed to enroll in { course.title }")

    return redirect("/")


@app.route('/add_course_ta/<courseID>' )
def add_ta_to_course(courseID):

    course = Course.query.get_or_404( courseID )

    if not (course in g.user.courses_teach_assisting):

        teach = Teaches(
            teaching_assistant_id = g.user.id,
            course_id = courseID
        )

        db.session.add( teach )
        db.session.commit()

        flash(f"Successfully added to { course.title }")
    
    else:
        flash(f"Failed to added to { course.title }")

    return redirect("/")


@app.route('/secretary/add/<courseID>' )
def add_secretary_to_course(courseID):

    course = Course.query.get_or_404( courseID )

    if not (course in g.user.courses_teach_assisting):

        secretary = Secretary(
            user_id = g.user.id,
            course_id = courseID
        )

        db.session.add( secretary )
        db.session.commit()

        flash(f"Successfully added to { course.title }")
    
    else:
        flash(f"Failed to added to { course.title }")

    return redirect("/secretary")
    


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage"""

    if g.user:
        courses = Course.query.all()
        return render_template('home.html', courses=courses)

    else:
        return redirect("/login")

@app.route('/error404')
def error_404():

    return render_template("error_404.html")


##############################################################################
# General user routes:

@app.route('/student_page/<enrollmentID>')
def student_enrollment_page(enrollmentID):
    """Show student roll"""

    student_enrollment = Enrollment.query.get_or_404(enrollmentID)
    form = InteractionsForm()

    if student_enrollment:
        return render_template("student_page.html", enrolled = student_enrollment, form=form)
    else:
        return redirect("/error404")


@app.route('/ta_page/<taID>')
def teaching_assistant_page(courseID):
    """Show TA's student management page"""

    course = Course.query.get_or_404( courseID )
    
    if course in g.user.courses_teach_assisting:

        roll = Enrollment.query.filter( 
            Enrollment.teaching_assistant_id == g.user.id).filter(
            courseID == Enrollment.course_id).all()

        return render_template("ta_page.html", current_course = course, roll = roll)

    else:
        return redirect("/error404")


@app.route('/secretary')
def general_secretary_page():
    """Show general secretary page"""

    if g.user.secretarying:

        return render_template("sec_page.html")
    
    else:

        return redirect("/error404")

