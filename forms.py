from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, \
    PasswordField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length


class InteractionsForm(FlaskForm):
    """Form for adding Interactions."""

    text = TextAreaField('text', validators=[DataRequired()])


class LessonForm(FlaskForm):
    """Form for adding assignments."""

    title = StringField('Lesson Title', validators=[DataRequired()])
    num = IntegerField('Number', validators=[DataRequired()])
    date_due = DateField('Date Due', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[Email()])
    phone = StringField('Phone', validators=[Length(min=7)])
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])