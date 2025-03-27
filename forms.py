from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from flask_login import current_user
from models import User
from app import db


class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=150)])
    username = StringField('username', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    dob = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    academic_qualification = SelectField('Academic Qualification', choices=[('', 'Select Academic Qualification'), ('SSC', 'SSC'), ('HSC', 'HSC'), ('UG', 'UG'), ('PG', 'PG'), ('PhD', 'PhD')],  validators=[DataRequired()])
    program = SelectField('Program', choices= [('', 'Select Program')], coerce= lambda x: int(x) if x else None, validators=[DataRequired()])
    discipline = SelectField('Discipline', choices= [('', 'Select Discipline')], coerce=lambda x: int(x) if x else None,validators=[Optional()])
    level = SelectField('Level', choices= [('', 'Select Level')], coerce=lambda x: int(x) if x else None, validators=[Optional()])
    gender = SelectField('Gender', choices=[('', 'Select Gender'),('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField('Register')

class ProfileUpdateForm(FlaskForm):
    username = StringField('Username (Email)', validators=[DataRequired(), Email(), Length(max=255)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=255)])
    qualification = SelectField('Academic Qualification', choices=[
        ('SSC', 'SSC'), ('HSC', 'HSC'), ('UG', 'UG'), ('PG', 'PG'), ('PhD', 'PhD')
    ], validators=[DataRequired()])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    program_id = SelectField('Program', coerce=int, validators=[DataRequired()])
    discipline_id = SelectField('Discipline', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    level_id = SelectField('Level', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField('Save')

    def validate_username(self, username):
        if username.data != current_user.username:
            existing_user = User.query.filter_by(username=username.data).first()
            if existing_user:
                raise ValidationError("This username (email) is already taken. Please choose another one.")