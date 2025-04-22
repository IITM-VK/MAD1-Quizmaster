# initialize_database.py
from app import app
from models import db, Admin, User, Program, Discipline, Level, Subject, Chapter, Quiz, Question, Score, Filter, RecentActivity, Feedback

# Initialize the database and populate it with data
with app.app_context():
    # Drop all existing tables (optional: only for resetting the database during development)
    db.drop_all()
    db.create_all()

    # Add a single admin
    admin = Admin(username="admin", password="798974")
    db.session.add(admin)

    # Add Programs
    program_bs = Program(
        name="BS Program",
        description="IITM Bachelor of Science (BS) Program for students pursuing higher education in specialized fields."
    )
    program_12 = Program(
        name="12th Program",
        description="12th-grade HSC curriculum covering Science, Commerce, and Arts."
    )
    program_10 = Program(
        name="10th Program",
        description="10th-grade SSC curriculum for foundational academic knowledge."
    )
    db.session.add_all([program_bs, program_12, program_10])

    # Add Disciplines for BS Program
    discipline_ds = Discipline(
        name="Data Science & Applications",
        program=program_bs,
        description="Specialization in Data Science, covering topics such as analytics, machine learning, and data visualization."
    )
    discipline_es = Discipline(
        name="Electronic Systems",
        program=program_bs,
        description="Focuses on electronic devices, circuits, and system-level design."
    )
    db.session.add_all([discipline_ds, discipline_es])

    # Add Levels for BS Program
    levels_ds = [
        Level(name="Foundation Level", discipline=discipline_ds, description="Introductory concepts in Data Science."),
        Level(name="Diploma in Data Science", discipline=discipline_ds, description="Core topics in Data Science."),
        Level(name="Diploma in Programming", discipline=discipline_ds, description="Specialized programming concepts."),
        Level(name="Degree Level", discipline=discipline_ds, description="Advanced studies in Data Science and Applications.")
    ]

    levels_es = [
        Level(name="Foundation Level", discipline=discipline_es, description="Introductory concepts in Electronic Systems."),
        Level(name="Diploma Level", discipline=discipline_es, description="Core topics in Electronic Systems."),
        Level(name="Degree Level", discipline=discipline_es, description="Advanced studies in Electronic Systems.")
    ]
    db.session.add_all(levels_ds + levels_es)

    # Add Disciplines for 12th Program
    discipline_science = Discipline(
        name="Science",
        program=program_12,
        description="Focus on subjects like Physics, Chemistry, Mathematics, and Biology."
    )
    discipline_commerce = Discipline(
        name="Commerce",
        program=program_12,
        description="Focus on subjects like Accountancy, Business Studies, and Economics."
    )
    discipline_arts = Discipline(
        name="Arts",
        program=program_12,
        description="Focus on subjects like History, Geography, Political Science, and Sociology."
    )
    db.session.add_all([discipline_science, discipline_commerce, discipline_arts])

    # Commit all changes to the database
    db.session.commit()
    print("Database initialized and populated with data successfully!")
