
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import os
import re
import docx2txt
from PyPDF2 import PdfReader

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['resume_analyzer_db']
users_collection = db['users']

def extract_text_from_resume(file_stream, filename):
    if filename.lower().endswith('.pdf'):
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    elif filename.lower().endswith('.docx'):
        return docx2txt.process(file_stream)
    return None

def analyze_resume(text):
    suggestions = []
    text_lower = text.lower()
    if 'skills' not in text_lower:
        suggestions.append("Add a Skills section to highlight your abilities.")
    if 'experience' not in text_lower:
        suggestions.append("Include your Work Experience section.")
    if 'education' not in text_lower:
        suggestions.append("Mention your educational background.")
    if not re.search(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', text_lower):
        suggestions.append("Include your email address for contact.")
    if len(text.split()) < 200:
        suggestions.append("Add more content to make your resume detailed.")
    if not suggestions:
        suggestions.append("Your resume looks good. Tailor it for each job you apply to.")
    return suggestions

def calculate_ats_score(text):
    keywords = ['skills', 'experience', 'education', 'email']
    score = sum(1 for keyword in keywords if keyword in text.lower())
    return (score / len(keywords)) * 100

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users_collection.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('dashboard'))

        flash("Invalid username or password.", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if not username or not password or not confirm:
            flash("Please fill in all fields.", "danger")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        elif users_collection.find_one({'username': username}):
            flash("Username already exists.", "danger")
        else:
            hashed = generate_password_hash(password)
            users_collection.insert_one({'username': username, 'password': hashed})
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))

    suggestions = ats_score = resume_text = None

    if request.method == 'POST':
        file = request.files.get('resume')
        if not file or file.filename == '':
            flash("Please upload a resume file.", "danger")
        else:
            text = extract_text_from_resume(file.stream, file.filename)
            if text:
                resume_text = text
                suggestions = analyze_resume(text)
                ats_score = calculate_ats_score(text)
            else:
                flash("Unsupported file type. Upload PDF or DOCX only.", "danger")

    return render_template('dashboard.html',
                           username=session['username'],
                           suggestions=suggestions,
                           ats_score=ats_score)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
