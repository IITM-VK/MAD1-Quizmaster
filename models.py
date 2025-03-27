from flask_sqlalchemy import SQLAlchemy
from app import app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from flask_login import UserMixin
from app import db

class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    @property
    def password(self):
        raise AttributeError('Password is not readable!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    academic_qualification = db.Column(db.String(255), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id'), nullable=True)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=True)
    gender = db.Column(db.String(10), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='active')
    profile_image_url = db.Column(db.String(255), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    date_joined = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # 🔹 Add relationships
    program = db.relationship('Program', backref='users')  
    discipline = db.relationship('Discipline', backref='users')
    level = db.relationship('Level', backref='users')

    @property
    def password(self):
        raise AttributeError('Password is not readable!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Program(db.Model):
    __tablename__ = 'program'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    disciplines = db.relationship('Discipline', backref='program', lazy=True, cascade="all, delete")
    subjects = db.relationship('Subject', backref='program', lazy=True, cascade="all, delete")


class Discipline(db.Model):
    __tablename__ = 'discipline'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id', ondelete="CASCADE"), nullable=False)
    description = db.Column(db.Text, nullable=True)
    levels = db.relationship('Level', backref='discipline', lazy=True, cascade="all, delete")
    subjects = db.relationship('Subject', backref='discipline', lazy=True, cascade="all, delete")


class Level(db.Model):
    __tablename__ = 'level'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id', ondelete="CASCADE"), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subjects = db.relationship('Subject', backref='level', lazy=True, cascade="all, delete")


class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id'), nullable=True)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=True)
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade="all, delete")


class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade="all, delete")


class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    total_marks = db.Column(db.Integer, nullable=False)
    passing_marks = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete")


class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    statement = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.String(255), nullable=False)
    option_2 = db.Column(db.String(255), nullable=False)
    option_3 = db.Column(db.String(255), nullable=False)
    option_4 = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)  # Values 1 to 4
    marks = db.Column(db.Integer, nullable=False)


class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp_attempted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_scored = db.Column(db.Integer, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # pass/fail
    date_attempted = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    total_questions = db.Column(db.Integer, nullable=False)
    attempts = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)  # Time in minutes


class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'quiz_id', name='unique_feedback'),
    )


class RecentActivity(db.Model):
    __tablename__ = 'recent_activities'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    activity_type = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    related_id = db.Column(db.Integer, nullable=False)
    entity_type = db.Column(db.String(255), nullable=False)  # Type of entity related to the activity


class Filter(db.Model):
    __tablename__ = 'filter'
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=True)
    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id'), nullable=True)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=True)
