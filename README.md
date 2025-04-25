# QuizVerse 🎓
A multi-user quiz application for exam preparation across various courses, built using Flask, Jinja2, SQLite, and Bootstrap.

---

## 💻 Demo

- Link to a live version (Please! Open in the Desktop)


  - Link(https://quizverse-tm9k.onrender.com)
aacb29c48cf7493f5f047a35c70485e440f0e146

---

## 🚀 About the Project

**QuizVerse** is a web-based quiz platform designed to support exam preparation through organized quizzes categorized under subjects and chapters. With dedicated roles for administrators and users, it provides a streamlined experience for quiz creation, management, and participation.

---

## 📌 Problem Statement

Build a multi-user quiz application that:
- Supports **admin** and **user** roles.
- Enables admins to create and manage **subjects**, **chapters**, **quizzes**, and **questions**.
- Allows users to register, log in, attempt quizzes, and view scores.
- Stores all data in an **SQLite** database.
- Uses **Flask** for backend and **Jinja2 templating with Bootstrap** for the front end.

---

## 🧑‍💼 Roles

### 👑 Admin (Quiz Master)
- Superuser with no registration required
- Can add/edit/delete:
  - Programs
  - Diciplines
  - Levels
  - Subjects
  - Chapters
  - Quizzes
  - MCQ-style questions
- Can manage users and view analytics

### 👤 User
- Can register/login with full profile info
- Can attempt quizzes and view scores
- Sees only user-appropriate dashboard and analytics

---

## 🧱 App Hierarchy

Programs → Disciplines → Levels → Subjects → Chapters → Quiz → Questions

---

## 💡 Core Features

- 🔐 **User & Admin Authentication**
- 🧾 **User Registration with Profile Info**
- 📚 **Subject & Chapter Management**
- 🧠 **Quiz Creation and Attempt**
- ⏱️ **Timer Functionality**
- 📊 **Score Recording and Summary Charts**
- 🗃️ **Fully Programmatic Database Setup**
- 📈 **ChartJS Integration for Analytics**

---

## 🛠️ Tech Stack

| Layer        | Technology                 |
|--------------|-----------------------------|
| Backend      | Flask, Flask-SQLAlchemy                       |
| Frontend     | Jinja2, HTML, CSS, Bootstrap, Javascript(Minimal) |
| Database     | SQLite                      |
| Charting     | ChartJS         |

---

## 🖼️ Screenshots

<p align="center">
  <img src="assets/Quizverse 1.png" alt="Image 1" width="45%"/>
  <img src="assets/Quizverse 2.png" alt="Image 1" width="45%"/>
  <img src="assets/Quizverse 3.png" alt="Image 1" width="45%"/>
  <img src="assets/Quizverse 4.png" alt="Image 1" width="45%"/>
</p>

---

## 📁 Folder Structure

```bash
quizverse/
│
├── assets/                # Screenshots of the app pages 
├── instance/              # Configuration files
    ├── db.sqlite3         # SQLite database (auto-generated)
├── migrations/            # DB migrations
├── static/                # CSS, JS, images, User Prifile pics
    ├── css
    ├── images
    ├── js
    ├── uploads/
        ├── profile_pics   
├── templates/             # HTML templates (Jinja2)
    ├── modals/
    ...
├── app.py                 # Main Flask entry point
├── config.py              # Configuration
├── forms.py               # WTForms / Flask-WTF forms
├── init_db.py             # Database initialization
├── License                # MIT License
├── models.py              # Database models
├── Quizmaster Report.pdf  # Project report file
├── README.md              # This file
├── requirements.txt       # Python dependencies
└── routes.py              # Flask route handlers
```
---

## ⚙️ Installation

1. Clone the Repository
```bash
git clone https://github.com/yourusername/quizverse.git
cd quizverse
```
2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
3. Install Dependencies
```bash
pip install -r requirements.txt
```
4. Run the Application
```bash
python app.py
```
---

## 🔧 Database Setup

All tables are programmatically created via model code. Manual DB creation is not allowed.
On first run, the application will initialize the database and seed it with the admin user.

---

## 📲 Usage

- Users can register, select subjects and chapters, and attempt available quizzes.
- Admin can manage all content and monitor quiz performance via dashboard.

---

## 🔐 Security & Validation

- Frontend validation using HTML5/JavaScript
- Backend validation for all form fields
- Use of Flask extensions like flask_login for secure sessions

---

## 🔗 APIs

REST APIs are optionally created for:
- Listing subjects, chapters, quizzes
- Returning JSON responses for dashboard analytics
| Implemented using flask_restful
---

## 📜 License
This project is licensed under the MIT License.
Feel free to fork, enhance, and build upon it.

---

## 👨‍💻 Author

Vivek Kumar

[GitHub](https://github.com/IITM-VK/) | [LinkedIn](https://www.linkedin.com/in/vivek-kumar-4b5a20231/)


##  <p align='center'> Thank You ❤️ </p>
