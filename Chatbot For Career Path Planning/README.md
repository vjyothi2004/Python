# Career Path Planner

An AI-powered web application that helps students and job seekers discover their perfect career path through intelligent chatbot interactions and personalized recommendations.

## 🚀 Features

- **AI-Powered Career Analysis**: Advanced NLP algorithms analyze skills, interests, and background
- **Interactive Chatbot**: Natural conversation flow with contextual responses
- **Personalized Career Pathways**: Customized recommendations based on user profile
- **Modern UI/UX**: Beautiful, responsive design with Tailwind CSS
- **User Authentication**: Secure login/signup system
- **Career Recommendations**: Dynamic career suggestions with detailed insights
- **Feedback System**: Rate and provide feedback on career suggestions
- **Mobile Responsive**: Works perfectly on all devices

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Authentication**: Session-based authentication
- **AI/NLP**: Custom keyword-based career matching algorithm
- **Icons**: Font Awesome
- **Styling**: Tailwind CSS (CDN)

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Chatbot_for_Career_Path_Planning
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 📁 Project Structure

```
Chatbot_for_Career_Path_Planning/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── templates/            # HTML templates
    ├── base.html         # Base template with navigation
    ├── index.html        # Home page
    ├── features.html     # Features page
    ├── login.html        # Login page
    ├── signup.html       # Signup page
    └── dashboard.html    # Main chatbot dashboard
```

## 🎯 How It Works

### 1. User Registration/Login
- Users can create accounts or sign in with existing credentials
- Session-based authentication ensures secure access

### 2. Interactive Chatbot
- Users interact with the AI chatbot through natural language
- The chatbot analyzes user input for keywords and interests
- Real-time career suggestions are provided based on the conversation

### 3. Career Matching Algorithm
The application uses a sophisticated keyword-based matching system:

- **Skill Keywords**: programming, coding, math, data, analysis, etc.
- **Interest Categories**: technology, business, creative, science, healthcare, etc.
- **Academic Background**: commerce, engineering, arts, science, etc.

### 4. Career Recommendations
- Dynamic career suggestions based on user input
- Detailed career descriptions and requirements
- Feedback system for continuous improvement

## 🎨 UI/UX Features

- **Modern Design**: Clean, professional interface with gradient backgrounds
- **Responsive Layout**: Works seamlessly on desktop, tablet, and mobile
- **Interactive Elements**: Hover effects, smooth transitions, and animations
- **User-Friendly Navigation**: Intuitive menu structure and breadcrumbs
- **Accessibility**: Proper contrast ratios and keyboard navigation

## 🔧 Customization

### Adding New Careers
To add new career paths, modify the `career_keywords` dictionary in `app.py`:

```python
career_keywords = {
    'new_skill': ['Career 1', 'Career 2', 'Career 3'],
    # ... existing keywords
}
```

### Modifying Career Categories
Update the `career_categories` dictionary to organize careers by field:

```python
career_categories = {
    'new_category': ['Career 1', 'Career 2', 'Career 3'],
    # ... existing categories
}
```

### Styling Changes
The application uses Tailwind CSS. You can customize colors, spacing, and other design elements by modifying the Tailwind classes in the HTML templates.

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
For production deployment, consider using:

1. **WSGI Server**: Gunicorn or uWSGI
2. **Reverse Proxy**: Nginx
3. **Environment Variables**: Set `FLASK_ENV=production`
4. **Database**: Replace in-memory storage with a proper database

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔒 Security Features

- Session-based authentication
- CSRF protection (Flask built-in)
- Input validation and sanitization
- Secure password handling
- XSS protection through proper HTML escaping

## 📊 Future Enhancements

- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Advanced NLP with machine learning models
- [ ] Resume builder functionality
- [ ] Job market analysis integration
- [ ] Email notifications
- [ ] Social login (Google, LinkedIn)
- [ ] Admin dashboard
- [ ] Analytics and reporting
- [ ] Multi-language support
- [ ] API endpoints for mobile apps

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/Chatbot_for_Career_Path_Planning/issues) page
2. Create a new issue with detailed information
3. Contact the development team

## 🙏 Acknowledgments

- Flask framework and community
- Tailwind CSS for the beautiful UI
- Font Awesome for icons
- All contributors and testers

---

**Made with ❤️ for helping people discover their perfect career path!** 