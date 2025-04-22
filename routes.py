from flask import render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Admin, User, Program, Discipline, Level, Subject, Chapter, Quiz, Question, Score, Filter, RecentActivity, Feedback
from app import app
from sqlalchemy.sql import text
from datetime import datetime, timedelta, timezone
from datetime import date
from werkzeug.utils import secure_filename
from forms import RegistrationForm, ProfileUpdateForm, ForgotPasswordForm, OTPForm, ResetPasswordForm
from functools import wraps
from flask_login import login_required, current_user, login_user, logout_user
import os
import smtplib
from email.mime.text import MIMEText
import random


# =================== Login Required Decorators ========================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            session.clear()
            flash("Please login as Admin to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or isinstance(current_user, Admin):
            flash("Please login to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

#================ Authentication Routes =============================
@app.route('/')
def login():
    return render_template('login.html')

# Combined Login Route for Admin and User
@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Try finding the user in Admin table first
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.verify_password(password):
            session.clear()
            session['user_type'] = 'admin'  # Store user type in session
            login_user(admin)
            flash("Welcome Admin!", "success")
            return redirect(url_for('admin_dashboard'))

        # Try finding the user in User table
        user = User.query.filter_by(username=username).first()
        if user:
            if not user.is_active:
                flash("Your account is inactive. Contact the administrator.", "error")
                return redirect(url_for('login'))

            if user.verify_password(password):
                session.clear()
                session['user_type'] = 'user'  # Store user type in session
                login_user(user)
                user.last_login = datetime.now(timezone.utc)  # Update last login time
                db.session.commit()
                flash("Login successful. Glad to have you back!", "success")
                return redirect(url_for('user_dashboard'))

            flash("Invalid password!", "error")
            return redirect(url_for('login'))

        # If no user or admin found
        flash("User not found! Please register first.", "error")
        return redirect(url_for('login'))

    return render_template('login.html')

# ================= Forgot password Route =========================

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(recipient_email, otp):
    sender_email = app.config['EMAIL_ADDRESS']
    sender_password = app.config['EMAIL_PASSWORD']
    smtp_server = app.config['SMTP_SERVER']
    smtp_port = app.config['SMTP_PORT']

    msg = MIMEText(f"Your OTP for password reset is: {otp}")
    msg['Subject'] = "Password Reset OTP"
    msg['From'] = sender_email
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.email.data).first()
        if user:
            otp = generate_otp()
            session['reset_email'] = user.username
            session['reset_otp'] = otp
            session['otp_time'] = datetime.utcnow().isoformat()
            if send_otp_email(user.username, otp):
                flash('OTP has been sent to your email.', 'success')
                return redirect(url_for('verify_otp'))
            else:
                flash('Error sending email.', 'error')
        else:
            flash('No user found with this email.', 'error')
    return render_template('forgot_password.html', form=form, stage='email')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reset_email' not in session:
        return redirect(url_for('forgot_password'))

    form = OTPForm()
    if form.validate_on_submit():
        entered_otp = form.otp.data
        if entered_otp == session.get('reset_otp'):
            flash('OTP verified! Please reset your password.', 'success')
            return redirect(url_for('reset_password'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
    return render_template('forgot_password.html', form=form, stage='otp')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_email' not in session:
        return redirect(url_for('forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=session['reset_email']).first()
        if user:
            user.password_hash = generate_password_hash(form.password.data)
            db.session.commit()
            session.pop('reset_email', None)
            session.pop('reset_otp', None)
            flash('Password changed successfully! You can login now.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error: User not found.', 'error')
    return render_template('forgot_password.html', form=form, stage='reset')

# ================ Fetch data from database ========================
@app.route('/get_programs')
def get_programs():
    programs = Program.query.all()
    program_list = [
        {
            "id": program.id,
            "name": program.name,
            "has_disciplines": bool(program.disciplines)  # Check if disciplines exist
        }
        for program in programs
    ]
    return jsonify(program_list)

@app.route('/get_disciplines/<int:program_id>')
def get_disciplines(program_id):
    disciplines = Discipline.query.filter_by(program_id=program_id).all()
    discipline_list = [
        {
            "id": discipline.id,
            "name": discipline.name,
            "has_levels": bool(discipline.levels)  # Check if levels exist
        }
        for discipline in disciplines
    ]
    return jsonify(discipline_list)

@app.route('/get_levels/<int:discipline_id>')
def get_levels(discipline_id):
    levels = Level.query.filter_by(discipline_id=discipline_id).all()
    level_list = [{"id": level.id, "name": level.name} for level in levels]
    return jsonify(level_list)

@app.route('/get_subjects')
def get_subjects():
    program_id = request.args.get("program_id", type=int)
    discipline_id = request.args.get("discipline_id", type=int)
    level_id = request.args.get("level_id", type=int)

    # Ensure at least one filter is applied
    if not any([program_id, discipline_id, level_id]):
        return jsonify([])  # Return empty list if no filters provided

    query = Subject.query
    if program_id:
        query = query.filter_by(program_id=program_id)
    if discipline_id:
        query = query.filter_by(discipline_id=discipline_id)
    if level_id:
        query = query.filter_by(level_id=level_id)

    subjects = query.all()
    subject_list = [{"id": subject.id, "name": subject.name} for subject in subjects]

    return jsonify(subject_list)

@app.route('/get_chapters/<int:subject_id>')
def get_chapters(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    chapter_list = [{"id": chapter.id, "name": chapter.name} for chapter in chapters]
    return jsonify(chapter_list)

@app.route('/get_quizzes/<int:chapter_id>')
def get_quizzes(chapter_id):
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    quiz_list = [{"id": quiz.id, "name": quiz.title} for quiz in quizzes]
    return jsonify(quiz_list)

# ====================== Registration Route =========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    form.program.choices = [(p.id, p.name) for p in Program.query.all()]
    form.discipline.choices = [('', 'Select Discipline')] + [(d.id, d.name) for d in Discipline.query.all()]
    form.level.choices = [('', 'Select Level')] + [(l.id, l.name) for l in Level.query.all()]

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'error')
            return redirect(url_for('register'))

        new_user = User(
            username=form.username.data,
            password=form.password.data,  
            full_name=form.full_name.data.title(),
            dob=form.dob.data,
            academic_qualification=form.academic_qualification.data,
            program_id=form.program.data,
            discipline_id=form.discipline.data if form.discipline.data else None,
            level_id=form.level.data if form.level.data else None,
            gender=form.gender.data,
            contact_number=form.contact_number.data
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# =================== Dashboard Routes =============================

# Admin dashboard route
@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    return render_template(
        "admin_dashboard.html",
        total_programs=Program.query.count(),
        total_disciplines=Discipline.query.count(),
        total_levels=Level.query.count(),
        total_subjects=Subject.query.count(),
        total_chapters=Chapter.query.count(),
        total_quizzes=Quiz.query.count(),
        total_questions=Question.query.count(),
        total_users=User.query.count(),

        programs=Program.query.all(),
        disciplines=Discipline.query.all(),
        levels=Level.query.all(),
        subjects=Subject.query.all(),
        chapters=Chapter.query.all(),
        quizzes=Quiz.query.all(),
        questions=Question.query.all(),
        users=User.query.all()
    )

# User dashboard route
@app.route('/user_dashboard')
@user_required
def user_dashboard():
    user = User.query.get(current_user.id)
    return render_template('user_dashboard.html', user=current_user, full_name=user.full_name if user else "User")

# Search Route
@app.route('/admin_search')
@admin_required
def admin_search():
    query = request.args.get('query', '').strip().lower()

    if not query:
        return redirect(url_for('admin_dashboard'))

    users = User.query.filter(User.username.ilike(f"%{query}%")).all()
    programs = Program.query.filter(Program.name.ilike(f"%{query}%")).all()
    disciplines = Discipline.query.filter(Discipline.name.ilike(f"%{query}%")).all()
    levels = Level.query.filter(Level.name.ilike(f"%{query}%")).all()
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    chapters = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()
    quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()

    return render_template("admin_search_results.html", query=query, users=users, programs=programs,
                            disciplines=disciplines, levels=levels, subjects=subjects, chapters=chapters, quizzes=quizzes)


@app.route('/user_search')
@user_required
def user_search():
    user = User.query.get(current_user.id)
    query = request.args.get('query', '').strip().lower()

    if not query:
        return redirect(url_for('user_dashboard'))

    programs = Program.query.filter(Program.name.ilike(f"%{query}%")).all()
    disciplines = Discipline.query.filter(Discipline.name.ilike(f"%{query}%")).all()
    levels = Level.query.filter(Level.name.ilike(f"%{query}%")).all()
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    chapters = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()
    quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()

    return render_template("user_search_results.html", query=query, programs=programs,
                            disciplines=disciplines, levels=levels, subjects=subjects, chapters=chapters, quizzes=quizzes, user=current_user, full_name=user.full_name if user else "User")

# Logout Route
@app.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('login'))

# Admin Logout Route
@app.route('/admin_logout')
@login_required
def admin_logout():
    session.clear() 
    logout_user()  
    flash("Admin logged out successfully.", "success")
    return redirect(url_for('login'))

# =================== Profile Page Routes==========================

UPLOAD_FOLDER = "static/uploads/profile_pics"
DEFAULT_PROFILE_PIC = "static/images/default_pic.jpg"

# Profile Route
@app.route('/profile', methods=['GET'])
@user_required
def profile():
    user = User.query.get(current_user.id)
    programs = Program.query.all()
    disciplines = Discipline.query.filter_by(program_id=user.program_id).all() if user.program_id else []
    levels = Level.query.filter_by(discipline_id=user.discipline_id).all() if user.discipline_id else []
    
    form = ProfileUpdateForm(obj=user)
    form.program_id.choices = [(p.id, p.name) for p in programs]
    form.discipline_id.choices = [('', 'Select Discipline')] + [(d.id, d.name) for d in disciplines]
    form.level_id.choices = [('', 'Select Level')] + [(l.id, l.name) for l in levels]

    return render_template('profile.html', form=form, user=current_user, full_name=user.full_name if user else "User", programs=programs)

# Update Profile Route
@app.route('/update_profile', methods=['POST'])
@user_required
def update_profile():
    user = User.query.get(current_user.id)
    form = ProfileUpdateForm(request.form)
    
    form.program_id.choices = [(p.id, p.name) for p in Program.query.all()]
    form.discipline_id.choices = [('', 'Select Discipline')] + [(d.id, d.name) for d in Discipline.query.all()]
    form.level_id.choices = [('', 'Select Level')] + [(l.id, l.name) for l in Level.query.all()]

    discipline_id = form.discipline_id.data if form.discipline_id.data else None
    level_id = form.level_id.data if form.level_id.data else None

    
    if form.validate():
        updated = False
        if form.username.data != user.username:
            user.username = form.username.data
            updated = True
        if form.full_name.data != user.full_name:
            user.full_name = form.full_name.data
            updated = True
        if form.qualification.data != user.academic_qualification:
            user.academic_qualification = form.qualification.data
            updated = True
        if form.dob.data and form.dob.data != user.dob:
            user.dob = form.dob.data
            updated = True
        if int(form.program_id.data) != user.program_id:
            user.program_id = int(form.program_id.data)
            updated = True
        if discipline_id != user.discipline_id:
            user.discipline_id = discipline_id
            updated = True
        if level_id != user.level_id:
            user.level_id = level_id
            updated = True
        if form.gender.data != user.gender:
            user.gender = form.gender.data
            updated = True
        if form.contact_number.data != user.contact_number:
            user.contact_number = form.contact_number.data
            updated = True
        
        if updated:
            db.session.commit()
            return jsonify({"success": True, "message": "Profile updated successfully!", "category": "success"})
        else:
            return jsonify({"success": False, "message": "No changes detected.", "category": "info"})

    return jsonify({"success": False, "message": "Invalid input data.", "category": "error"})

# Profile Picture Upload Route
@app.route('/upload_profile_pic', methods=['POST'])
@user_required
def upload_profile_pic():
    if 'profile_pic' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded.", "category": "error"})

    file = request.files['profile_pic']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected.", "category": "error"})

    filename = secure_filename(f"user_{current_user.id}.jpg")
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Delete old profile pic if exists
    if current_user.profile_image_url and "uploads/profile_pics" in current_user.profile_image_url:
        old_path = os.path.join(app.root_path, current_user.profile_image_url.lstrip('/'))
        if os.path.exists(old_path):
            os.remove(old_path)

    file.save(file_path)

    current_user.profile_image_url = url_for('static', filename=f'uploads/profile_pics/{filename}')
    db.session.commit()

    return jsonify({
        "success": True, 
        "message": "Profile picture updated successfully!", 
        "category": "success",
        "image_url": current_user.profile_image_url
    })


# Profile Picture Delete Route
@app.route('/delete_profile_pic', methods=['POST'])
@user_required
def delete_profile_pic():
    if current_user.profile_image_url and "uploads/profile_pics" in current_user.profile_image_url:
        old_path = os.path.join(app.root_path, current_user.profile_image_url.lstrip('/'))
        if os.path.exists(old_path):
            os.remove(old_path)

    current_user.profile_image_url = None
    db.session.commit()

    return jsonify({
        "success": True, 
        "message": "Profile picture deleted successfully!", 
        "category": "success",
        "image_url": url_for('static', filename='images/default_pic.jpg')
    })


#  ======================= Test Route =============================
@app.route('/test', methods=['GET'])
@user_required
def test():
    user = User.query.get(current_user.id)

    # Fetch filter values from request args
    program_id = request.args.get('program_id')
    discipline_id = request.args.get('discipline_id')
    level_id = request.args.get('level_id')
    subject_id = request.args.get('subject_id')
    chapter_id = request.args.get('chapter_id')

    # Fetch available options for filters
    programs = Program.query.all()
    disciplines = Discipline.query.all()
    levels = Level.query.all()
    subjects = Subject.query.all()
    chapters = Chapter.query.all()

    # Base query for quizzes
    query = Quiz.query.join(Chapter).join(Subject)

    # Apply filters dynamically
    if program_id:
        query = query.filter(Subject.program_id == program_id)
    if discipline_id:
        query = query.filter(Subject.discipline_id == discipline_id)
    if level_id:
        query = query.filter(Subject.level_id == level_id)
    if subject_id:
        query = query.filter(Quiz.chapter.has(subject_id=subject_id))
    if chapter_id:
        query = query.filter(Quiz.chapter_id == chapter_id)

    quizzes = query.all()

    return render_template(
        'test.html',
        user=user,
        full_name=user.full_name if user else "User",
        programs=programs,
        disciplines=disciplines,
        levels=levels,
        subjects=subjects,
        chapters=chapters,
        quizzes=quizzes,
        current_date=date.today()
    )

# ======== Test Details Route ============
@app.route('/view_test_details/<int:quiz_id>')
@user_required
def view_test_details(quiz_id):
    user = User.query.get(current_user.id)
    quiz = Quiz.query.get_or_404(quiz_id)
    total_questions = Question.query.filter_by(quiz_id=quiz_id).count()
    return render_template('view_test_details.html', user=user, full_name=user.full_name if user else "User", quiz=quiz, total_questions=total_questions)

# ========= Quiz Attempt Route =============
@app.route('/launch_test/<int:quiz_id>')
@user_required
def launch_test(quiz_id):
    """ Renders the quiz attempt page with all necessary data """
    user = User.query.get(current_user.id)
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if quiz is accessible today
    if quiz.date_of_quiz != date.today():
        flash("This quiz is not available today.", "warning")
        return redirect(url_for('test'))

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    return render_template('launch_test.html', user=user, quiz=quiz, questions=questions)

@app.route('/submit_quiz', methods=['POST'])
@user_required
def submit_quiz():
    data = request.json
    quiz_id = data.get('quiz_id')
    user_id = current_user.id
    answers = data.get('answers', {})
    time_taken = data.get('timeTaken',0)
    attempts = data.get("attempts", 0)

    if not quiz_id:
        return jsonify({"error": "Missing quiz ID"}), 400

    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    total_marks = sum(q.marks for q in questions)
    correct_answers = 0
    total_scored = 0 

    for q in questions:
        question_id = str(q.id)  # Ensure consistency with JS object keys
        user_answer = answers.get(question_id, None) 

        if user_answer is not None:  #  Only count attempted questions
            if int(user_answer) == q.correct_option:
                correct_answers += 1
                total_scored += q.marks

    # **Check if the user already has an existing score record**
    existing_score = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()

    if existing_score:
        # **Update the existing score instead of inserting a new one**
        existing_score.total_scored = total_scored
        existing_score.status = 'pass' if total_scored >= quiz.passing_marks else 'fail'
        existing_score.date_attempted = datetime.utcnow().date()
        existing_score.total_questions = len(questions)
        existing_score.attempts = attempts
        existing_score.correct_answers = correct_answers
        existing_score.time_taken = time_taken
    else:
        # **Create a new score entry if no previous record exists**
        new_score = Score(
            quiz_id=quiz_id,
            user_id=user_id,
            total_scored=total_scored,
            total_marks=total_marks,
            status='pass' if total_scored >= quiz.passing_marks else 'fail',
            date_attempted=datetime.utcnow().date(),
            total_questions=len(questions),
            attempts=attempts,
            correct_answers=correct_answers,
            time_taken=time_taken
        )
        db.session.add(new_score)

    db.session.commit()

    return jsonify({"message": "Quiz submitted successfully", "score": total_scored, "redirect": url_for('test')})

# ==================== Performance Route =========================
@app.route('/performance')
@user_required
def performance():
    user = User.query.get(current_user.id)
    scores = (Score.query
                .join(Quiz)
                .join(Chapter, Quiz.chapter_id == Chapter.id)
                .join(Subject, Chapter.subject_id == Subject.id)
                .filter(Score.user_id == current_user.id)
                .all())
    return render_template('performance.html', scores=scores, user=user, full_name=user.full_name if user else "User")

@app.route('/get_scores', methods=['GET'])
@user_required
def get_scores():
    user_id = current_user.id
    scores = Score.query.filter_by(user_id=user_id).all()

    score_data = [{
        "quiz_title": getattr(s.quiz, 'title', 'N/A'),
        "date_attempted": s.date_attempted.strftime('%d-%m-%Y'),
        "subject": getattr(s.quiz.chapter.subject, 'name', 'N/A'),
        "chapter": getattr(s.quiz.chapter, 'name', 'N/A'),
        "questions": s.total_questions,
        "attempts": s.attempts,
        "correct": s.correct_answers,
        "accuracy": round((s.correct_answers / s.total_questions) * 100, 2) if s.total_questions > 0 else 0,
        "total_marks": s.total_marks,
        "score": s.total_scored,
        "percentage": round((s.total_scored / s.total_marks) * 100, 2) if s.total_marks > 0 else 0,
        "status": s.status
    } for s in scores]
    return jsonify(score_data)

@app.route('/get_performance_summary', methods=['GET'])
@user_required
def get_performance_summary():
    user_id = current_user.id
    scores = Score.query.filter_by(user_id=user_id).all()

    subject_quiz_count = {}
    month_quiz_count = {}
    month_performance = {}

    for s in scores:
        subject_name = s.quiz.chapter.subject.name
        month = s.date_attempted.strftime('%Y-%m')
        
        subject_quiz_count[subject_name] = subject_quiz_count.get(subject_name, 0) + 1
        month_quiz_count[month] = month_quiz_count.get(month, 0) + 1
        
        if month not in month_performance:
            month_performance[month] = {'total_score': 0, 'total_marks': 0}
        
        month_performance[month]['total_score'] += s.total_scored
        month_performance[month]['total_marks'] += s.total_marks

    return jsonify({
        "subjects": list(subject_quiz_count.keys()),
        "quiz_counts": list(subject_quiz_count.values()),
        "months": list(month_quiz_count.keys()),
        "month_counts": list(month_quiz_count.values()),
        "dates": list(month_performance.keys()),
        "scores": [round((data['total_score'] / data['total_marks']) * 100, 2) if data['total_marks'] > 0 else 0 for data in month_performance.values()]
    })

# ==================== PROGRAMS, DISCIPLINES & LEVELS ====================

@app.route('/programs_disciplines_levels')
@admin_required
def programs_disciplines_levels():
    programs = Program.query.all()
    disciplines = Discipline.query.all()
    levels = Level.query.all()
    
    return render_template('programs_disciplines_levels.html', 
                            programs=programs, 
                            disciplines=disciplines, 
                            levels=levels)

# ========== Add Actions ==========
@app.route('/add_program', methods=['POST'])
@admin_required
def add_program():
    name = request.form.get("name")
    description = request.form.get("description")

    if not name:
        flash("Program name is required", "error")
        return redirect(url_for('programs_disciplines_levels', tab='programs'))

    new_program = Program(name=name, description=description)
    db.session.add(new_program)
    db.session.commit()

    flash("Program added successfully!", "success")
    return redirect(url_for('programs_disciplines_levels', tab='programs'))

@app.route('/add_discipline', methods=['POST'])
@admin_required
def add_discipline():
    name = request.form.get("name")
    description = request.form.get("description")
    program_id = request.form.get("program")

    if not name or not program_id:
        flash("Discipline name and Program are required", "error")
        return redirect(url_for('programs_disciplines_levels', tab='disciplines'))

    new_discipline = Discipline(name=name, description=description, program_id=program_id)
    db.session.add(new_discipline)
    db.session.commit()

    flash("Discipline added successfully!", "success")
    return redirect(url_for('programs_disciplines_levels', tab='disciplines'))

@app.route('/add_level', methods=['POST'])
@admin_required
def add_level():
    name = request.form.get("name")
    description = request.form.get("description")
    discipline_id = request.form.get("discipline")

    if not name or not discipline_id:
        flash("Level name and Discipline are required", "error")
        return redirect(url_for('programs_disciplines_levels', tab='levels'))

    new_level = Level(name=name, description=description, discipline_id=discipline_id)
    db.session.add(new_level)
    db.session.commit()

    flash("Level added successfully!", "success")
    return redirect(url_for('programs_disciplines_levels', tab='levels'))

# ========== Edit Actions ==========
@app.route('/edit_program/<int:id>', methods=['POST'])
@admin_required
def edit_program(id):
    program = Program.query.get(id)
    if not program:
        flash("Program not found!", "error")
        return redirect(url_for('programs_disciplines_levels', tab='programs'))

    program.name = request.form.get("name")
    program.description = request.form.get("description")
    db.session.commit()

    flash("Program updated successfully!", "success")
    return redirect(url_for('programs_disciplines_levels', tab='programs'))

@app.route('/edit_discipline/<int:id>', methods=['POST'])
@admin_required
def edit_discipline(id):
    discipline = Discipline.query.get(id)
    if not discipline:
        flash("Discipline not found!", "error")
        return redirect(url_for('programs_disciplines_levels', tab='disciplines'))

    discipline.name = request.form.get("name")
    discipline.program_id = request.form.get("program")
    discipline.description = request.form.get("description")
    db.session.commit()

    flash("Discipline updated successfully!", "success")
    return redirect(url_for('programs_disciplines_levels', tab='disciplines'))

@app.route('/edit_level/<int:id>', methods=['POST'])
@admin_required
def edit_level(id):
    level = Level.query.get(id)
    if not level:
        flash("Level not found!", "error")
        return redirect(url_for('programs_disciplines_levels', tab='levels'))

    level.name = request.form.get("name")
    level.discipline_id = request.form.get("discipline")
    level.description = request.form.get("description")
    db.session.commit()

    flash("Level updated successfully!", "success")
    return redirect(url_for('programs_disciplines_levels', tab='levels'))

# ========== Delete Actions ==========
@app.route('/delete_program/<int:id>', methods=['POST'])
@admin_required
def delete_program(id):
    program = Program.query.get(id)
    if not program:
        flash("Program not found!", "error")
        return redirect(url_for('programs_disciplines_levels', tab='programs'))

    db.session.delete(program)
    db.session.commit()

    flash("Program and all related disciplines and levels deleted successfully!", "success")
    return redirect(url_for('programs_disciplines_levels', tab='programs'))

@app.route('/delete_discipline/<int:id>', methods=['POST'])
@admin_required
def delete_discipline(id):
    discipline = Discipline.query.get(id)
    if not discipline:
        flash("Discipline not found!", "error")
        return redirect(url_for('programs_disciplines_levels', tab='disciplines'))


    db.session.delete(discipline)
    db.session.commit()

    flash("Discipline and all related levels deleted successfully!", "success")
    return redirect(url_for('programs_disciplines_levels', tab='disciplines'))

@app.route('/delete_level/<int:id>', methods=['POST'])
@admin_required
def delete_level(id):
    level = Level.query.get(id)
    if not level:
        flash("Level not found!", "error")
        return redirect(url_for('programs_disciplines_levels', tab='levels'))

    db.session.delete(level)
    db.session.commit()

    flash("Level deleted successfully!", "success")
    return redirect(url_for('programs_disciplines_levels', tab='levels'))

# ==================== SUBJECTS & CHAPTERS ====================

@app.route('/subjects_chapters', methods=['GET'])
@admin_required
def subjects_chapters():
    # Get filter values from query parameters
    program_id = request.args.get('program', type=int)
    discipline_id = request.args.get('discipline', type=int)
    level_id = request.args.get('level', type=int)
    subject_id = request.args.get('subject', type=int)

    # Query subjects based on filters
    subjects_query = Subject.query
    if program_id:
        subjects_query = subjects_query.filter_by(program_id=program_id)
    if discipline_id:
        subjects_query = subjects_query.filter_by(discipline_id=discipline_id)
    if level_id:
        subjects_query = subjects_query.filter_by(level_id=level_id)

    subjects = subjects_query.all()

    # Query chapters based on filters
    chapters_query = Chapter.query
    if subject_id:
        chapters_query = chapters_query.filter_by(subject_id=subject_id)

    chapters = chapters_query.all()

    return render_template(
        'subjects_chapters.html',
        subjects=subjects,
        chapters=chapters,
        programs=Program.query.all(),
        disciplines=Discipline.query.all(),
        levels=Level.query.all()
    )

# ========== Add Actions ==========
@app.route('/add_subject', methods=['POST'])
@admin_required
def add_subject():
    name = request.form.get("name")
    description = request.form.get("description")
    program_id = request.form.get("program")
    discipline_id = request.form.get("discipline") or None
    level_id = request.form.get("level") or None

    if not name or not program_id:
        flash("Subject name and program are required!", "error")
        return redirect(url_for('subjects_chapters', tab='subjects'))

    new_subject = Subject(
        name=name, 
        description=description,
        program_id=program_id,
        discipline_id=discipline_id,
        level_id=level_id
    )
    db.session.add(new_subject)
    db.session.commit()

    flash("Subject added successfully!", "success")
    return redirect(url_for('subjects_chapters', tab='subjects'))

@app.route('/add_chapter', methods=['POST'])
@admin_required
def add_chapter():
    name = request.form.get("name")
    description = request.form.get("description")
    subject_id = request.form.get("subject")

    if not name or not subject_id:
        flash("Chapter name and subject are required!", "error")
        return redirect(url_for('subjects_chapters', tab='chapters'))

    new_chapter = Chapter(
        name=name,
        description=description,
        subject_id=subject_id
    )
    db.session.add(new_chapter)
    db.session.commit()

    flash("Chapter added successfully!", "success")
    return redirect(url_for('subjects_chapters', tab='chapters'))

# ========== Edit Actions ==========
@app.route('/edit_subject/<int:id>', methods=['POST'])
@admin_required
def edit_subject(id):
    subject = Subject.query.get_or_404(id)

    subject.name = request.form.get("name")
    subject.description = request.form.get("description")
    subject.program_id = request.form.get("program")
    subject.discipline_id = request.form.get("discipline") or None
    subject.level_id = request.form.get("level") or None

    db.session.commit()

    flash("Subject updated successfully!", "success")
    return redirect(url_for('subjects_chapters', tab='subjects'))

@app.route('/edit_chapter/<int:id>', methods=['POST'])
@admin_required
def edit_chapter(id):
    chapter = Chapter.query.get_or_404(id)

    chapter.name = request.form.get("name")
    chapter.description = request.form.get("description")
    chapter.subject_id = request.form.get("subject")

    db.session.commit()

    flash("Chapter updated successfully!", "success")
    return redirect(url_for('subjects_chapters', tab='chapters'))

# ========== Delete Actions ==========
@app.route('/delete_subject/<int:id>', methods=['POST'])
@admin_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)

    # Deleting related chapters automatically
    db.session.delete(subject)
    db.session.commit()

    flash("Subject and its related chapters deleted successfully!", "success")
    return redirect(url_for('subjects_chapters', tab='subjects'))

@app.route('/delete_chapter/<int:id>', methods=['POST'])
@admin_required
def delete_chapter(id):
    chapter = Chapter.query.get_or_404(id)

    db.session.delete(chapter)
    db.session.commit()

    flash("Chapter deleted successfully!", "success")
    return redirect(url_for('subjects_chapters', tab='chapters'))

# ==================== QUIZZES & QUESTIONS ====================

@app.route('/quiz_management', methods=['GET'])
@admin_required
def quiz_management():
    # Get filter values from query parameters
    program_id = request.args.get('program', type=int)
    discipline_id = request.args.get('discipline', type=int)
    level_id = request.args.get('level', type=int)
    subject_id = request.args.get('subject', type=int)
    chapter_id = request.args.get('chapter', type=int)
    quiz_id = request.args.get('quiz', type=int)

    # Query quizzes based on filters
    quizzes_query = Quiz.query
    if chapter_id:
        quizzes_query = quizzes_query.filter_by(chapter_id=chapter_id)
    elif subject_id:
        quizzes_query = quizzes_query.join(Chapter).filter(Chapter.subject_id == subject_id)
    elif level_id:
        quizzes_query = quizzes_query.join(Chapter, Subject).filter(Subject.level_id == level_id)
    elif discipline_id:
        quizzes_query = quizzes_query.join(Chapter, Subject).filter(Subject.discipline_id == discipline_id)
    elif program_id:
        quizzes_query = quizzes_query.join(Chapter, Subject).filter(Subject.program_id == program_id)

    quizzes = quizzes_query.all()

    # Query questions based on filters
    questions_query = Question.query
    if quiz_id:
        questions_query = questions_query.filter_by(quiz_id=quiz_id)
    elif chapter_id:
        questions_query = questions_query.join(Quiz).filter(Quiz.chapter_id == chapter_id)
    elif subject_id:
        questions_query = questions_query.join(Quiz, Chapter).filter(Chapter.subject_id == subject_id)
    elif level_id:
        questions_query = questions_query.join(Quiz, Chapter, Subject).filter(Subject.level_id == level_id)
    elif discipline_id:
        questions_query = questions_query.join(Quiz, Chapter, Subject).filter(Subject.discipline_id == discipline_id)
    elif program_id:
        questions_query = questions_query.join(Quiz, Chapter, Subject).filter(Subject.program_id == program_id)

    questions = questions_query.all()

    return render_template(
        "quiz_management.html",
        quizzes=quizzes,
        questions=questions,
        programs=Program.query.all(),
        disciplines=Discipline.query.all(),
        levels=Level.query.all(),
        subjects=Subject.query.all(),
        chapters=Chapter.query.all()
    )

# ========== Add Actions ==========
@app.route('/add_quiz', methods=['POST'])
@admin_required
def add_quiz():
    title = request.form.get("title")
    chapter_id = request.form.get("chapter_id")
    date_of_quiz_str = request.form.get("date_of_quiz")
    time_duration = request.form.get("time_duration")
    total_marks = request.form.get("total_marks")
    passing_marks = request.form.get("passing_marks")
    description = request.form.get("description")

    if not title or not chapter_id:
        flash("Quiz title and chapter are required!", "error")
        return redirect(url_for('quiz_management', tab='quizzes'))
    
    try:
        date_of_quiz = datetime.strptime(date_of_quiz_str, "%Y-%m-%d").date()  # Convert to date
    except ValueError:
        flash("Invalid date format!", "error")
        return redirect(url_for('quiz_management', tab='quizzes'))

    new_quiz = Quiz(
        title=title,
        chapter_id=chapter_id,
        date_of_quiz=date_of_quiz,
        time_duration=time_duration,
        total_marks=total_marks,
        passing_marks=passing_marks,
        description=description
    )
    db.session.add(new_quiz)
    db.session.commit()

    flash("Quiz added successfully!", "success")
    return redirect(url_for('quiz_management', tab='quizzes'))

@app.route('/add_question', methods=['POST'])
@admin_required
def add_question():
    title = request.form.get("title")
    quiz_id = request.form.get("quiz_id")
    statement = request.form.get("statement")
    option_1 = request.form.get("option_1")
    option_2 = request.form.get("option_2")
    option_3 = request.form.get("option_3")
    option_4 = request.form.get("option_4")
    correct_option = request.form.get("correct_option")
    marks = request.form.get("marks")

    if not title or not quiz_id:
        flash("Question title and quiz are required!", "error")
        return redirect(url_for('quiz_management', tab='questions'))

    new_question = Question(
        title=title,
        quiz_id=quiz_id,
        statement=statement,
        option_1=option_1,
        option_2=option_2,
        option_3=option_3,
        option_4=option_4,
        correct_option=correct_option,
        marks=marks
    )
    db.session.add(new_question)
    db.session.commit()

    flash("Question added successfully!", "success")
    return redirect(url_for('quiz_management', tab='questions'))

# ========== Edit Actions ==========
@app.route('/edit_quiz/<int:id>', methods=['POST'])
@admin_required
def edit_quiz(id):
    quiz = Quiz.query.get_or_404(id)

    quiz.title = request.form.get("title")
    quiz.chapter_id = request.form.get("chapter_id")
    quiz.date_of_quiz_str = request.form.get("date_of_quiz")
    quiz.time_duration = request.form.get("time_duration")
    quiz.total_marks = request.form.get("total_marks")
    quiz.passing_marks = request.form.get("passing_marks")
    quiz.description = request.form.get("description")
    
    try:
        quiz.date_of_quiz = datetime.strptime(quiz.date_of_quiz_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format!", "error")
        return redirect(url_for('quiz_management', tab='quizzes'))

    db.session.commit()
    flash("Quiz updated successfully!", "success")
    return redirect(url_for('quiz_management', tab='quizzes'))

@app.route('/edit_question/<int:id>', methods=['POST'])
@admin_required
def edit_question(id):
    question = Question.query.get_or_404(id)

    question.title = request.form.get("title")
    question.quiz_id = request.form.get("quiz_id")
    question.statement = request.form.get("statement")
    question.option_1 = request.form.get("option_1")
    question.option_2 = request.form.get("option_2")
    question.option_3 = request.form.get("option_3")
    question.option_4 = request.form.get("option_4")
    question.correct_option = request.form.get("correct_option")
    question.marks = request.form.get("marks")

    db.session.commit()
    flash("Question updated successfully!", "success")
    return redirect(url_for('quiz_management', tab='questions'))

# ========== Delete Actions ==========
@app.route('/delete_quiz/<int:id>', methods=['POST'])
@admin_required
def delete_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    db.session.delete(quiz)
    db.session.commit()

    flash("Quiz deleted successfully!", "success")
    return redirect(url_for('quiz_management', tab='quizzes'))

@app.route('/delete_question/<int:id>', methods=['POST'])
@admin_required
def delete_question(id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()

    flash("Question deleted successfully!", "success")
    return redirect(url_for('quiz_management', tab='questions'))

# ==================== Admin Summary ====================

@app.route('/admin_summary')
@admin_required
def admin_summary():
    # Fetch Subject-Wise Top Scores (Following Subject → Chapter → Quiz → Score)
    top_scores = db.session.query(
        Subject.name.label("subject_name"),
        db.func.max(Score.total_scored).label("score")
    ).join(Chapter, Chapter.subject_id == Subject.id) \
    .join(Quiz, Quiz.chapter_id == Chapter.id) \
    .join(Score, Score.quiz_id == Quiz.id) \
    .group_by(Subject.id) \
    .order_by(db.func.max(Score.total_scored).desc()).all()

    top_scores_labels = [record.subject_name for record in top_scores]
    top_scores_values = [record.score for record in top_scores]

    # Fetch Subject-Wise User Attempts (Following Subject → Chapter → Quiz → Score)
    user_attempts = db.session.query(
        Subject.name.label("subject_name"),
        db.func.count(Score.id).label("total_attempts")
    ).join(Chapter, Chapter.subject_id == Subject.id) \
    .join(Quiz, Quiz.chapter_id == Chapter.id) \
    .join(Score, Score.quiz_id == Quiz.id) \
    .group_by(Subject.id) \
    .all()

    user_attempts_labels = [record.subject_name for record in user_attempts]
    user_attempts_values = [record.total_attempts for record in user_attempts]

    # Fetch Active and Inactive Users
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    active_users = User.query.filter(User.last_login >= seven_days_ago).count()
    inactive_users = User.query.filter(User.last_login < thirty_days_ago).count()

    return render_template("admin_summary.html",
                            top_scores_labels=top_scores_labels,
                            top_scores_values=top_scores_values,
                            user_attempts_labels=user_attempts_labels,
                            user_attempts_values=user_attempts_values,
                            active_users=active_users,
                            inactive_users=inactive_users)

# ==================== User Management ====================

@app.route('/user_management')
@admin_required
def user_management():
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')

    # Get all regular users (excluding admins)
    admin_usernames = [admin.username for admin in Admin.query.all()]
    users_query = User.query.filter(~User.username.in_(admin_usernames))  # Exclude admin usernames

    if search_query:
        users_query = users_query.filter(User.username.ilike(f'%{search_query}%'))

    if status_filter == 'active':
        users_query = users_query.filter(User.is_active == True)
    elif status_filter == 'inactive':
        users_query = users_query.filter(User.is_active == False)

    users = users_query.order_by(User.last_login.desc().nulls_last()).all()
    
    return render_template("user_management.html", users=users)

@app.route('/toggle_user_status/<int:user_id>')
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)

    # Toggle active status
    user.set_status(not user.is_active)
    db.session.commit()
    flash("User status updated successfully!", "success")
    return redirect(url_for('user_management'))

@app.route('/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent deleting admin accounts
    if Admin.query.filter_by(username=user.username).first():
        flash("Cannot delete the admin account!", "danger")
        return redirect(url_for('user_management'))
    
    if user.profile_image_url and "uploads/profile_pics" in user.profile_image_url:
        image_path = os.path.join(app.root_path, user.profile_image_url.lstrip('/'))
        if os.path.exists(image_path):
            os.remove(image_path)
            
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!", "success")
    return redirect(url_for('user_management'))

# ===================================================== End of the file ===================================================