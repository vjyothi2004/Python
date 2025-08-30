from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import re
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'career_planner_secret_key_2024'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# File-based user storage for persistence
USERS_FILE = 'users.json'

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_users(users_data):
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users_data, f, indent=2)
    except Exception as e:
        print(f"Error saving users: {e}")

# Load existing users
users = load_users()

# Session-based conversation tracking
conversation_states = {}

# Conversation flow questions
conversation_questions = [
    {
        'id': 'skills',
        'question': "Let's start with your skills and strengths! What are you good at? (e.g., 'I'm good at coding', 'I have strong communication skills', 'I'm great at problem solving')",
        'keywords': ['coding', 'programming', 'communication', 'problem solving', 'math', 'writing', 'design', 'analysis', 'leadership', 'creativity']
    },
    {
        'id': 'interests',
        'question': "Great! Now tell me what you enjoy doing. What activities or subjects do you love? (e.g., 'I love working with data', 'I enjoy creative projects', 'I like helping people', 'I'm passionate about technology')",
        'keywords': ['data', 'creative', 'helping', 'technology', 'science', 'business', 'art', 'music', 'teaching', 'research']
    },
    {
        'id': 'background',
        'question': "Perfect! What's your academic or professional background? (e.g., 'I studied business', 'I have experience in marketing', 'I'm a recent graduate', 'I worked in healthcare')",
        'keywords': ['business', 'marketing', 'healthcare', 'engineering', 'arts', 'science', 'education', 'finance', 'technology', 'design']
    },
    {
        'id': 'goals',
        'question': "Excellent! Finally, what are your career goals or what kind of work environment do you prefer? (e.g., 'I want to work in tech', 'I prefer creative environments', 'I like helping people', 'I want to work remotely')",
        'keywords': ['tech', 'creative', 'helping', 'remote', 'team', 'leadership', 'innovation', 'stability', 'growth', 'impact']
    }
]

# Topic-specific career mappings for more targeted recommendations
topic_careers = {
    'programming & development': [
        'Software Engineer',
        'Web Developer', 
        'Mobile App Developer',
        'DevOps Engineer',
        'Full Stack Developer',
        'Backend Developer',
        'Frontend Developer',
        'Game Developer',
        'Software Architect',
        'QA Engineer'
    ],
    'data & analytics': [
        'Data Scientist',
        'Data Analyst',
        'Business Intelligence Analyst',
        'Machine Learning Engineer',
        'Statistician',
        'Data Engineer',
        'Database Administrator',
        'Business Analyst',
        'Market Research Analyst',
        'Operations Analyst'
    ],
    'communication & marketing': [
        'Marketing Manager',
        'Digital Marketing Specialist',
        'Social Media Manager',
        'Content Creator',
        'Public Relations Specialist',
        'Brand Manager',
        'SEO Specialist',
        'Communications Manager',
        'Sales Manager',
        'Influencer Manager'
    ],
    'business & finance': [
        'Business Analyst',
        'Financial Analyst',
        'Accountant',
        'Project Manager',
        'Management Consultant',
        'Investment Banker',
        'Financial Advisor',
        'Operations Manager',
        'Product Manager',
        'Risk Analyst'
    ],
    'creative & design': [
        'UI/UX Designer',
        'Graphic Designer',
        'Product Designer',
        'Creative Director',
        'Art Director',
        'Web Designer',
        'Illustrator',
        'Animator',
        'Video Editor',
        'Content Creator'
    ],
    'healthcare & helping': [
        'Healthcare Administrator',
        'Nurse',
        'Medical Assistant',
        'Health Educator',
        'Public Health Specialist',
        'Social Worker',
        'Counselor',
        'Human Resources Manager',
        'Customer Success Manager',
        'Community Manager'
    ],
    'teaching & education': [
        'Teacher',
        'Professor',
        'Educational Consultant',
        'Curriculum Developer',
        'Training Specialist',
        'Educational Administrator',
        'Instructional Designer',
        'Academic Advisor',
        'Education Policy Analyst',
        'Corporate Trainer'
    ],
    'research & science': [
        'Research Scientist',
        'Data Scientist',
        'Laboratory Technician',
        'Environmental Scientist',
        'Biotechnologist',
        'Medical Researcher',
        'Academic Researcher',
        'Policy Analyst',
        'Market Research Analyst',
        'Science Teacher'
    ]
}

# Career mapping based on keywords and interests
career_keywords = {
    'programming': ['Software Engineer', 'Web Developer', 'Data Scientist', 'DevOps Engineer', 'Mobile App Developer'],
    'coding': ['Software Engineer', 'Web Developer', 'Data Scientist', 'DevOps Engineer', 'Mobile App Developer'],
    'code': ['Software Engineer', 'Web Developer', 'Data Scientist', 'DevOps Engineer', 'Mobile App Developer'],
    'software': ['Software Engineer', 'Web Developer', 'DevOps Engineer', 'QA Engineer', 'Product Manager'],
    'developer': ['Software Engineer', 'Web Developer', 'Mobile App Developer', 'DevOps Engineer'],
    'math': ['Data Scientist', 'Actuary', 'Financial Analyst', 'Statistician', 'Research Analyst'],
    'mathematics': ['Data Scientist', 'Actuary', 'Financial Analyst', 'Statistician', 'Research Analyst'],
    'statistics': ['Data Scientist', 'Statistician', 'Research Analyst', 'Business Analyst', 'Market Research Analyst'],
    'data': ['Data Scientist', 'Data Analyst', 'Business Intelligence Analyst', 'Database Administrator', 'Machine Learning Engineer'],
    'analytics': ['Data Analyst', 'Business Analyst', 'Financial Analyst', 'Market Research Analyst', 'Operations Analyst'],
    'analysis': ['Data Analyst', 'Business Analyst', 'Financial Analyst', 'Market Research Analyst', 'Operations Analyst'],
    'business': ['Business Analyst', 'Management Consultant', 'Project Manager', 'Marketing Manager', 'Sales Manager'],
    'commerce': ['Accountant', 'Financial Analyst', 'Business Analyst', 'Marketing Manager', 'Sales Manager'],
    'marketing': ['Marketing Manager', 'Digital Marketing Specialist', 'Brand Manager', 'Content Creator', 'SEO Specialist'],
    'design': ['UI/UX Designer', 'Graphic Designer', 'Web Designer', 'Product Designer', 'Creative Director'],
    'creative': ['Graphic Designer', 'Content Creator', 'Creative Director', 'Art Director', 'Copywriter'],
    'writing': ['Content Writer', 'Copywriter', 'Technical Writer', 'Journalist', 'Editor'],
    'communication': ['Public Relations Specialist', 'Communications Manager', 'Content Creator', 'Marketing Manager', 'Sales Representative'],
    'sales': ['Sales Manager', 'Sales Representative', 'Account Executive', 'Business Development Manager', 'Sales Analyst'],
    'finance': ['Financial Analyst', 'Accountant', 'Investment Banker', 'Financial Advisor', 'Risk Analyst'],
    'accounting': ['Accountant', 'Financial Analyst', 'Auditor', 'Tax Consultant', 'Bookkeeper'],
    'health': ['Healthcare Administrator', 'Nurse', 'Medical Assistant', 'Health Educator', 'Public Health Specialist'],
    'healthcare': ['Healthcare Administrator', 'Nurse', 'Medical Assistant', 'Health Educator', 'Public Health Specialist'],
    'medical': ['Doctor', 'Nurse', 'Medical Assistant', 'Healthcare Administrator', 'Medical Researcher'],
    'helping': ['Nurse', 'Healthcare Administrator', 'Health Educator', 'Social Worker', 'Counselor'],
    'people': ['Nurse', 'Healthcare Administrator', 'Social Worker', 'Counselor', 'Human Resources Manager'],
    'science': ['Research Scientist', 'Laboratory Technician', 'Science Teacher', 'Environmental Scientist', 'Biotechnologist'],
    'research': ['Research Scientist', 'Data Scientist', 'Market Research Analyst', 'Academic Researcher', 'Policy Analyst'],
    'teaching': ['Teacher', 'Professor', 'Educational Consultant', 'Curriculum Developer', 'Training Specialist'],
    'education': ['Teacher', 'Educational Administrator', 'Curriculum Developer', 'Educational Consultant', 'Training Specialist'],
    'management': ['Project Manager', 'Operations Manager', 'Product Manager', 'General Manager', 'Team Lead'],
    'leadership': ['Project Manager', 'Team Lead', 'Department Manager', 'Executive', 'Management Consultant'],
    'customer': ['Customer Success Manager', 'Customer Service Representative', 'Account Manager', 'Client Relations Specialist'],
    'support': ['Technical Support Specialist', 'Customer Service Representative', 'Help Desk Analyst', 'IT Support Specialist'],
    'technology': ['IT Manager', 'Systems Administrator', 'Network Engineer', 'Cybersecurity Analyst', 'Technology Consultant'],
    'tech': ['IT Manager', 'Systems Administrator', 'Network Engineer', 'Cybersecurity Analyst', 'Technology Consultant'],
    'network': ['Network Engineer', 'Network Administrator', 'Cybersecurity Analyst', 'Systems Administrator', 'IT Manager'],
    'security': ['Cybersecurity Analyst', 'Information Security Specialist', 'Security Engineer', 'Compliance Officer', 'Risk Analyst'],
    'art': ['Graphic Designer', 'Art Director', 'Creative Director', 'Illustrator', 'Animator'],
    'music': ['Music Producer', 'Sound Engineer', 'Music Teacher', 'Composer', 'Audio Engineer'],
    'video': ['Video Editor', 'Content Creator', 'Film Producer', 'Multimedia Specialist', 'Video Producer'],
    'social': ['Social Media Manager', 'Digital Marketing Specialist', 'Community Manager', 'Content Creator', 'Influencer Manager'],
    'media': ['Social Media Manager', 'Content Creator', 'Digital Marketing Specialist', 'Media Planner', 'Public Relations Specialist'],
    'content': ['Content Creator', 'Content Writer', 'Copywriter', 'Social Media Manager', 'Digital Marketing Specialist'],
    'project': ['Project Manager', 'Product Manager', 'Program Manager', 'Operations Manager'],
    'product': ['Product Manager', 'Product Designer', 'Product Marketing Manager', 'Business Analyst'],
    'user': ['UI/UX Designer', 'Product Designer', 'User Experience Designer', 'Interaction Designer'],
    'experience': ['UI/UX Designer', 'User Experience Designer', 'Customer Experience Manager', 'Product Manager'],
    'interface': ['UI/UX Designer', 'User Interface Designer', 'Frontend Developer', 'Product Designer'],
    'frontend': ['Frontend Developer', 'UI/UX Designer', 'Web Developer', 'User Interface Designer'],
    'backend': ['Backend Developer', 'Software Engineer', 'Database Administrator', 'DevOps Engineer'],
    'fullstack': ['Full Stack Developer', 'Software Engineer', 'Web Developer', 'DevOps Engineer'],
    'mobile': ['Mobile App Developer', 'Software Engineer', 'UI/UX Designer', 'Product Manager'],
    'app': ['Mobile App Developer', 'Software Engineer', 'Web Developer', 'Product Manager'],
    'web': ['Web Developer', 'Frontend Developer', 'Backend Developer', 'Full Stack Developer'],
    'database': ['Database Administrator', 'Data Engineer', 'Backend Developer', 'Data Scientist'],
    'cloud': ['Cloud Engineer', 'DevOps Engineer', 'Systems Administrator', 'Software Engineer'],
    'devops': ['DevOps Engineer', 'Site Reliability Engineer', 'Cloud Engineer', 'Systems Administrator'],
    'machine': ['Machine Learning Engineer', 'Data Scientist', 'AI Engineer', 'Research Scientist'],
    'learning': ['Machine Learning Engineer', 'Data Scientist', 'AI Engineer', 'Educational Consultant'],
    'artificial': ['AI Engineer', 'Machine Learning Engineer', 'Data Scientist', 'Research Scientist'],
    'intelligence': ['AI Engineer', 'Machine Learning Engineer', 'Data Scientist', 'Business Intelligence Analyst'],
    'ai': ['AI Engineer', 'Machine Learning Engineer', 'Data Scientist', 'Research Scientist'],
    'ml': ['Machine Learning Engineer', 'Data Scientist', 'AI Engineer', 'Research Scientist']
}

# Career categories for broader matching
career_categories = {
    'technology': ['Software Engineer', 'Web Developer', 'Data Scientist', 'DevOps Engineer', 'Mobile App Developer', 'IT Manager', 'Systems Administrator', 'Network Engineer', 'Cybersecurity Analyst'],
    'business': ['Business Analyst', 'Management Consultant', 'Project Manager', 'Marketing Manager', 'Sales Manager', 'Accountant', 'Financial Analyst', 'Operations Manager'],
    'creative': ['UI/UX Designer', 'Graphic Designer', 'Content Creator', 'Creative Director', 'Art Director', 'Copywriter', 'Video Editor', 'Animator'],
    'science': ['Data Scientist', 'Research Scientist', 'Statistician', 'Laboratory Technician', 'Environmental Scientist', 'Biotechnologist', 'Medical Researcher'],
    'healthcare': ['Healthcare Administrator', 'Nurse', 'Medical Assistant', 'Health Educator', 'Public Health Specialist', 'Doctor', 'Medical Researcher'],
    'education': ['Teacher', 'Professor', 'Educational Consultant', 'Curriculum Developer', 'Training Specialist', 'Educational Administrator'],
    'finance': ['Financial Analyst', 'Accountant', 'Investment Banker', 'Financial Advisor', 'Risk Analyst', 'Actuary', 'Auditor'],
    'marketing': ['Marketing Manager', 'Digital Marketing Specialist', 'Brand Manager', 'Content Creator', 'SEO Specialist', 'Social Media Manager', 'Public Relations Specialist']
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Reload users from file to ensure we have the latest data
        current_users = load_users()
        
        print(f"Login attempt for email: {email}")
        print(f"Available users: {list(current_users.keys())}")
        
        if email in current_users and current_users[email]['password'] == password:
            session['user'] = email
            session['username'] = current_users[email]['name']
            session.permanent = True  # Make session persistent
            print(f"Login successful for user: {current_users[email]['name']}")
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            print(f"Login failed for email: {email}")
            if email not in current_users:
                flash('Email not registered. Please sign up first.', 'error')
            else:
                flash('Invalid password. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        print(f"Signup attempt for email: {email}, name: {name}")
        
        # Reload users from file to ensure we have the latest data
        current_users = load_users()
        
        if not all([name, email, password, confirm_password]):
            flash('All fields are required', 'error')
        elif password != confirm_password:
            flash('Passwords do not match', 'error')
        elif email in current_users:
            flash('Email already registered', 'error')
        else:
            # Add new user
            current_users[email] = {
                'name': name,
                'password': password,
                'created_at': datetime.now().isoformat()
            }
            
            # Save to file
            save_users(current_users)
            
            # Update global users variable
            global users
            users = current_users
            
            print(f"User created successfully: {email}")
            print(f"Total users in system: {len(current_users)}")
            
            # Set session
            session['user'] = email
            session['username'] = name
            session.permanent = True  # Make session persistent
            flash('Account created successfully!', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please login to access the dashboard', 'error')
        return redirect(url_for('login'))
    
    # Verify user still exists in storage
    current_users = load_users()
    if session['user'] not in current_users:
        session.clear()
        flash('User account not found. Please login again.', 'error')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', username=session['username'])

@app.route('/api/chat', methods=['POST'])
def chat():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    user_message = data.get('message', '').lower()
    user_id = session['user']
    
    # Initialize conversation state for new users
    if user_id not in conversation_states:
        conversation_states[user_id] = {
            'current_question': 0,
            'profile': {},
            'in_conversation': True
        }
    
    # Check if user is asking about a specific career
    career_details = get_career_details(user_message)
    if career_details:
        return jsonify({
            'response': career_details,
            'careers': []
        })
    
    # Check if user wants to restart the conversation
    if any(phrase in user_message for phrase in ['restart', 'start over', 'begin again', 'new conversation']):
        conversation_states[user_id] = {
            'current_question': 0,
            'profile': {},
            'in_conversation': True
        }
        return jsonify({
            'response': conversation_questions[0]['question'],
            'careers': []
        })
    
    # Check if user wants to start the conversation flow
    if any(phrase in user_message for phrase in ['yes', 'start conversation', 'begin', 'start', 'okay', 'sure']):
        if user_id not in conversation_states or not conversation_states[user_id]['in_conversation']:
            conversation_states[user_id] = {
                'current_question': 0,
                'profile': {},
                'in_conversation': True
            }
            return jsonify({
                'response': conversation_questions[0]['question'],
                'careers': []
            })
    
    # Handle conversation flow
    if conversation_states[user_id]['in_conversation']:
        current_q = conversation_states[user_id]['current_question']
        
        # If we're still in the question flow
        if current_q < len(conversation_questions):
            # Store the user's answer
            question_id = conversation_questions[current_q]['id']
            conversation_states[user_id]['profile'][question_id] = user_message
            
            # Move to next question
            conversation_states[user_id]['current_question'] += 1
            
            # If there are more questions, ask the next one
            if conversation_states[user_id]['current_question'] < len(conversation_questions):
                next_question = conversation_questions[conversation_states[user_id]['current_question']]['question']
                return jsonify({
                    'response': next_question,
                    'careers': []
                })
            else:
                # All questions answered, generate career recommendations
                conversation_states[user_id]['in_conversation'] = False
                return generate_profile_based_recommendations(user_id)
    
    # If not in conversation flow, use the existing topic/keyword matching
    return handle_regular_chat(user_message)

def generate_profile_based_recommendations(user_id):
    """Generate career recommendations based on the user's complete profile"""
    profile = conversation_states[user_id]['profile']
    
    # Analyze the profile and extract key themes
    all_responses = ' '.join(profile.values()).lower()
    
    # Count keyword matches for each topic
    topic_scores = {}
    
    for topic, careers in topic_careers.items():
        score = 0
        topic_keywords = get_topic_keywords(topic)
        for keyword in topic_keywords:
            if keyword in all_responses:
                score += 1
        topic_scores[topic] = score
    
    # Get top 2-3 topics
    sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    top_topics = [topic for topic, score in sorted_topics if score > 0][:3]
    
    # Generate response
    if top_topics:
        response = "Based on your complete profile, here are the career paths that best match your skills, interests, and background:\n\n"
        
        all_recommended_careers = []
        for topic in top_topics:
            careers = topic_careers[topic][:3]  # Top 3 from each topic
            all_recommended_careers.extend(careers)
        
        # Remove duplicates and limit to 8 careers
        unique_careers = list(dict.fromkeys(all_recommended_careers))[:8]
        
        for i, career in enumerate(unique_careers, 1):
            response += f"{i}. **{career}**\n"
        
        response += "\n**Why these careers match your profile:**\n"
        
        # Explain why each topic matches
        for topic in top_topics[:2]:
            topic_name = topic.replace(' & ', ' and ')
            response += f"• **{topic_name}**: Your profile shows strong alignment with this field\n"
        
        response += "\nWould you like to know more about any of these specific careers, or would you like to explore other options?"
        
        return jsonify({
            'response': response,
            'careers': unique_careers
        })
    else:
        # Fallback if no clear matches
        response = "Thank you for sharing your profile! Based on your responses, here are some diverse career options that might interest you:\n\n"
        fallback_careers = [
            'Business Analyst', 'Project Manager', 'Content Creator', 
            'Data Analyst', 'Marketing Specialist', 'Customer Success Manager'
        ]
        
        for i, career in enumerate(fallback_careers, 1):
            response += f"{i}. **{career}**\n"
        
        response += "\nWould you like to know more about any of these careers, or would you like to restart the conversation to get more specific recommendations?"
        
        return jsonify({
            'response': response,
            'careers': fallback_careers
        })

def get_topic_keywords(topic):
    """Get relevant keywords for each topic"""
    topic_keywords = {
        'programming & development': ['coding', 'programming', 'software', 'developer', 'code', 'tech', 'technology'],
        'data & analytics': ['data', 'analytics', 'statistics', 'analysis', 'math', 'numbers', 'research'],
        'communication & marketing': ['communication', 'marketing', 'social', 'media', 'content', 'brand', 'writing'],
        'business & finance': ['business', 'finance', 'accounting', 'management', 'commerce', 'money', 'economics'],
        'creative & design': ['creative', 'design', 'art', 'graphic', 'visual', 'drawing', 'painting'],
        'healthcare & helping': ['health', 'medical', 'helping', 'people', 'care', 'nursing', 'doctor'],
        'teaching & education': ['teaching', 'education', 'learning', 'instructor', 'trainer', 'school'],
        'research & science': ['research', 'science', 'laboratory', 'scientific', 'experiment', 'study']
    }
    return topic_keywords.get(topic, [])

def handle_regular_chat(user_message):
    """Handle regular chat when not in conversation flow"""
    # First, check for topic-specific matches (highest priority)
    found_careers = set()
    matched_topics = []
    
    # Topic-specific matching
    topic_mappings = {
        'programming & development': ['like coding', 'programming', 'software development', 'coding', 'developer'],
        'data & analytics': ['working with data', 'analytics', 'data analysis', 'statistics', 'data'],
        'communication & marketing': ['communication', 'marketing', 'social media', 'content', 'brand'],
        'business & finance': ['business', 'finance', 'accounting', 'management', 'commerce'],
        'creative & design': ['creative', 'design', 'art', 'graphic', 'visual'],
        'healthcare & helping': ['healthcare', 'helping people', 'medical', 'health', 'care'],
        'teaching & education': ['teaching', 'education', 'learning', 'instructor', 'trainer'],
        'research & science': ['research', 'science', 'laboratory', 'scientific', 'experiment']
    }
    
    for topic, keywords in topic_mappings.items():
        if any(keyword in user_message for keyword in keywords):
            if topic in topic_careers:
                found_careers.update(topic_careers[topic])
                matched_topics.append(topic)
    
    # If no topic-specific matches, fall back to keyword matching
    if not found_careers:
        # Extract keywords from user message with improved matching
        matched_keywords = []
        
        # Enhanced keyword matching with word boundaries and variations
        message_words = user_message.split()
        
        # Check for exact keyword matches and word variations
        for keyword, careers in career_keywords.items():
            # Check if keyword is in message (exact match)
            if keyword in user_message:
                found_careers.update(careers)
                matched_keywords.append(keyword)
            # Check if any word in message contains the keyword
            elif any(keyword in word or word in keyword for word in message_words):
                found_careers.update(careers)
                matched_keywords.append(keyword)
        
        # If no specific keywords found, try category matching
        if not found_careers:
            for category, careers in career_categories.items():
                if category in user_message:
                    found_careers.update(careers)
                    matched_keywords.append(category)
        
        # Additional context-based matching for common phrases
        context_keywords = {
            'like coding': ['programming', 'software'],
            'good at math': ['math', 'statistics', 'data'],
            'enjoy working with data': ['data', 'analysis'],
            'strong communication': ['communication', 'marketing'],
            'studied business': ['business', 'commerce'],
            'love creative': ['creative', 'design', 'art'],
            'interested in technology': ['technology', 'programming'],
            'passionate about design': ['design', 'creative'],
            'enjoy marketing': ['marketing', 'communication'],
            'love finance': ['finance', 'accounting'],
            'interested in healthcare': ['health', 'medical'],
            'enjoy teaching': ['teaching', 'education'],
            'love research': ['research', 'science'],
            'interested in sales': ['sales', 'business'],
            'enjoy writing': ['writing', 'content'],
            'love music': ['music', 'creative'],
            'interested in video': ['video', 'creative'],
            'enjoy social media': ['social', 'media'],
            'love art': ['art', 'creative'],
            'interested in security': ['security', 'technology'],
            'helping people': ['helping', 'people', 'health'],
            'working with people': ['helping', 'people', 'communication'],
            'passionate about helping': ['helping', 'people', 'health'],
            'love working with': ['helping', 'people', 'communication'],
            'enjoy helping': ['helping', 'people', 'health'],
            'good at helping': ['helping', 'people', 'health'],
            'love science': ['science', 'research'],
            'passionate about science': ['science', 'research'],
            'enjoy science': ['science', 'research'],
            'love education': ['education', 'teaching'],
            'passionate about education': ['education', 'teaching'],
            'enjoy education': ['education', 'teaching'],
            'love teaching': ['teaching', 'education'],
            'passionate about teaching': ['teaching', 'education'],
            'enjoy teaching': ['teaching', 'education']
        }
        
        # Check for context-based matches
        for phrase, keywords in context_keywords.items():
            if phrase in user_message:
                for keyword in keywords:
                    if keyword in career_keywords:
                        found_careers.update(career_keywords[keyword])
                        if keyword not in matched_keywords:
                            matched_keywords.append(keyword)
    
    # Generate response
    if found_careers:
        careers_list = list(found_careers)[:5]  # Limit to 5 suggestions
        
        # Create a more personalized response based on whether it's topic-specific or keyword-based
        if matched_topics:
            # Topic-specific response
            topic_name = matched_topics[0].replace(' & ', ' and ')
            response = f"Based on your interest in {topic_name}, here are some excellent career paths that could be perfect for you:\n\n"
        else:
            # Keyword-based response
            if len(matched_keywords) == 1:
                response = f"Based on your interest in {matched_keywords[0]}, here are some excellent career paths that could be perfect for you:\n\n"
            else:
                response = f"Based on your interests in {', '.join(matched_keywords[:-1])} and {matched_keywords[-1]}, here are some career paths that combine these skills:\n\n"
        
        for i, career in enumerate(careers_list, 1):
            response += f"{i}. **{career}**\n"
        
        response += "\nThese careers align well with your background and interests. Would you like to know more about any of these specific roles, or would you like to explore other options based on different aspects of your profile?"
    else:
        # Offer to start the conversation flow
        response = "I'd love to help you find the perfect career path! I can ask you a few questions to understand your profile better and give you personalized recommendations.\n\n"
        response += "Would you like to start a guided conversation where I ask you about:\n"
        response += "• Your skills and strengths\n"
        response += "• What you enjoy doing\n"
        response += "• Your background\n"
        response += "• Your career goals\n\n"
        response += "Just say 'yes' or 'start conversation' to begin, or try one of the suggested topics on the left!"
    
    return jsonify({
        'response': response,
        'careers': list(found_careers)[:5] if found_careers else []
    })

def get_career_details(message):
    """Provide detailed information about specific careers"""
    career_info = {
        'software engineer': {
            'title': 'Software Engineer',
            'description': 'Software Engineers design, develop, and maintain software applications and systems.',
            'skills': 'Programming languages (Python, Java, JavaScript), Data structures & algorithms, Software design patterns, Version control (Git), Database management',
            'education': 'Bachelor\'s degree in Computer Science, Software Engineering, or related field',
            'career_path': 'Junior Developer → Senior Developer → Lead Developer → Software Architect → Engineering Manager',
            'salary_range': '$70,000 - $150,000+ annually',
            'job_outlook': 'Excellent - High demand with strong growth projected',
            'companies': 'Google, Microsoft, Amazon, Apple, Meta, startups'
        },
        'data scientist': {
            'title': 'Data Scientist',
            'description': 'Data Scientists analyze complex data sets to help organizations make data-driven decisions.',
            'skills': 'Python/R, Statistics, Machine Learning, SQL, Data visualization, Big data tools (Hadoop, Spark)',
            'education': 'Master\'s degree in Data Science, Statistics, Computer Science, or related field',
            'career_path': 'Data Analyst → Data Scientist → Senior Data Scientist → Lead Data Scientist → Chief Data Officer',
            'salary_range': '$80,000 - $160,000+ annually',
            'job_outlook': 'Excellent - Rapidly growing field with high demand',
            'companies': 'Netflix, Uber, Airbnb, Google, Amazon, consulting firms'
        },
        'web developer': {
            'title': 'Web Developer',
            'description': 'Web Developers create and maintain websites and web applications.',
            'skills': 'HTML, CSS, JavaScript, React/Angular/Vue, Node.js, Database management, API development',
            'education': 'Bachelor\'s degree in Computer Science, Web Development, or self-taught with portfolio',
            'career_path': 'Junior Developer → Frontend/Backend Developer → Full Stack Developer → Senior Developer → Tech Lead',
            'salary_range': '$50,000 - $120,000+ annually',
            'job_outlook': 'Very Good - Consistent demand for web development skills',
            'companies': 'Tech companies, agencies, startups, freelance opportunities'
        },
        'marketing manager': {
            'title': 'Marketing Manager',
            'description': 'Marketing Managers develop and execute marketing strategies to promote products or services.',
            'skills': 'Digital marketing, Market research, Brand management, Analytics, Communication, Project management',
            'education': 'Bachelor\'s degree in Marketing, Business, or Communications',
            'career_path': 'Marketing Coordinator → Marketing Specialist → Marketing Manager → Senior Marketing Manager → Marketing Director',
            'salary_range': '$60,000 - $130,000+ annually',
            'job_outlook': 'Good - Steady growth in digital marketing roles',
            'companies': 'Consumer brands, agencies, tech companies, startups'
        },
        'business analyst': {
            'title': 'Business Analyst',
            'description': 'Business Analysts analyze business processes and recommend improvements.',
            'skills': 'Business process modeling, Data analysis, Requirements gathering, Stakeholder management, SQL, Excel',
            'education': 'Bachelor\'s degree in Business, IT, or related field',
            'career_path': 'Business Analyst → Senior Business Analyst → Lead Business Analyst → Business Analysis Manager',
            'salary_range': '$55,000 - $110,000+ annually',
            'job_outlook': 'Good - Growing demand for business analysis skills',
            'companies': 'Consulting firms, corporations, government agencies'
        },
        'graphic designer': {
            'title': 'Graphic Designer',
            'description': 'Graphic Designers create visual content for various media platforms.',
            'skills': 'Adobe Creative Suite, Typography, Color theory, Layout design, Brand identity, Digital design',
            'education': 'Bachelor\'s degree in Graphic Design, Fine Arts, or portfolio-based',
            'career_path': 'Junior Designer → Graphic Designer → Senior Designer → Art Director → Creative Director',
            'salary_range': '$40,000 - $90,000+ annually',
            'job_outlook': 'Good - Growing demand in digital design',
            'companies': 'Design agencies, in-house teams, freelance opportunities'
        },
        'financial analyst': {
            'title': 'Financial Analyst',
            'description': 'Financial Analysts analyze financial data and provide investment guidance.',
            'skills': 'Financial modeling, Excel, Accounting, Investment analysis, Risk assessment, Market research',
            'education': 'Bachelor\'s degree in Finance, Accounting, Economics, or related field',
            'career_path': 'Financial Analyst → Senior Financial Analyst → Finance Manager → Director of Finance',
            'salary_range': '$55,000 - $120,000+ annually',
            'job_outlook': 'Good - Stable demand in finance sector',
            'companies': 'Banks, investment firms, corporations, consulting firms'
        },
        'project manager': {
            'title': 'Project Manager',
            'description': 'Project Managers plan and oversee projects to ensure they are completed on time and within budget.',
            'skills': 'Project planning, Risk management, Team leadership, Communication, Agile/Scrum, Budget management',
            'education': 'Bachelor\'s degree in Business, IT, or related field; PMP certification recommended',
            'career_path': 'Project Coordinator → Project Manager → Senior Project Manager → Program Manager → Portfolio Manager',
            'salary_range': '$60,000 - $140,000+ annually',
            'job_outlook': 'Very Good - High demand across industries',
            'companies': 'IT companies, construction, healthcare, government agencies'
        },
        'ui/ux designer': {
            'title': 'UI/UX Designer',
            'description': 'UI/UX Designers design user interfaces and experiences for digital products.',
            'skills': 'User research, Wireframing, Prototyping, Visual design, Usability testing, Design tools (Figma, Sketch)',
            'education': 'Bachelor\'s degree in Design, HCI, or related field',
            'career_path': 'Junior Designer → UI/UX Designer → Senior Designer → Design Lead → Head of Design',
            'salary_range': '$50,000 - $120,000+ annually',
            'job_outlook': 'Excellent - High demand in tech industry',
            'companies': 'Tech companies, design agencies, startups, freelance'
        },
        'content creator': {
            'title': 'Content Creator',
            'description': 'Content Creators create engaging content for various platforms and audiences.',
            'skills': 'Content writing, Social media, Video editing, Photography, SEO, Analytics',
            'education': 'Bachelor\'s degree in Communications, Marketing, or portfolio-based',
            'career_path': 'Content Creator → Senior Content Creator → Content Manager → Content Director',
            'salary_range': '$35,000 - $100,000+ annually',
            'job_outlook': 'Good - Growing demand for digital content',
            'companies': 'Media companies, brands, agencies, freelance opportunities'
        }
    }
    
    # Check if message contains career names
    for career_key, career_data in career_info.items():
        if career_key in message or career_data['title'].lower() in message:
            response = f"**{career_data['title']}**\n\n"
            response += f"**Description:** {career_data['description']}\n\n"
            response += f"**Required Skills:** {career_data['skills']}\n\n"
            response += f"**Education:** {career_data['education']}\n\n"
            response += f"**Typical Career Path:** {career_data['career_path']}\n\n"
            response += f"**Salary Range:** {career_data['salary_range']}\n\n"
            response += f"**Job Outlook:** {career_data['job_outlook']}\n\n"
            response += f"**Top Companies:** {career_data['companies']}\n\n"
            response += "Would you like to know about similar careers or explore other options?"
            return response
    
    return None

@app.route('/api/feedback', methods=['POST'])
def feedback():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    feedback_type = data.get('type')  # 'helpful' or 'not_helpful'
    career = data.get('career')
    
    # In a real application, you would store this feedback in a database
    # For now, we'll just acknowledge it
    return jsonify({'message': 'Thank you for your feedback!'})

# Debug route to view users (remove in production)
@app.route('/debug/users')
def debug_users():
    current_users = load_users()
    return jsonify({
        'total_users': len(current_users),
        'users': list(current_users.keys()),
        'session_user': session.get('user'),
        'session_username': session.get('username')
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 