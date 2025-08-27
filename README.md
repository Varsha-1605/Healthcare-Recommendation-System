# HealthAI - AI-Powered Healthcare Platform

A comprehensive healthcare recommendation platform that combines Flask backend with modern frontend technologies. Features real-time AI-powered personalized health recommendations using Gemini AI, medical NLP models, and a sophisticated recommendation system.

## 🚀 Features

- **AI-Powered Health Recommendations**: Personalized health content using Gemini AI
- **Symptom Analysis**: Advanced AI consultation with medical entity extraction
- **Real-time Updates**: WebSocket connections for live recommendations
- **Advanced Analytics**: Health insights dashboard with predictive analytics
- **User Management**: Secure authentication and comprehensive health profiles
- **Content Management**: Categorized health articles, videos, exercises, and treatments

## 📋 Requirements

Create a `requirements.txt` file with the following dependencies:

```txt
flask==3.0.0
flask-sqlalchemy==3.1.1
flask-socketio==5.3.6
werkzeug==3.0.1
google-genai==0.3.1
pydantic==2.5.0
requests==2.31.0
psycopg2-binary==2.9.9
gunicorn==21.2.0
eventlet==0.33.3
python-socketio==5.10.0
```
## 🎥 Project Demo

<iframe src="https://drive.google.com/file/d/11Xo26uHHepyUvrRQNZuaaYfJOErOLuDN/preview" 
        width="640" 
        height="480" 
        allow="autoplay">
</iframe>


## 🛠️ Local Setup Instructions

### 1. Clone or Create Project Directory

```bash
mkdir HealthAI
cd HealthAI
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the root directory:

```env
# Required API Keys
GEMINI_API_KEY=your_gemini_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///healthcare_ai.db

# Flask Configuration
SESSION_SECRET=your-secret-key-here
FLASK_ENV=development
```

### 5. Initialize Database

```bash
python -c "from app import db; db.create_all(); print('Database tables created')"
```

### 6. Run the Application

```bash
python main.py
```

The application will be available at `http://localhost:5000`

## 🗂️ Project Structure

```
HealthAI/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── favicon.ico
│   └── js/
│       ├── analytics.js
│       ├── main.js
│       └── websocket.js
├── templates/
│   ├── 404.html
│   ├── analytics.html
│   ├── base.html
│   ├── consultation.html
│   ├── consultation_history.html
│   ├── content_detail.html
│   ├── dashboard.html
│   ├── index.html
│   ├── login.html
│   ├── profile.html
│   ├── register.html
│   └── search.html
├── ai_services.py          # AI/ML integration services
├── app.py                  # Flask application setup
|__ gunicorn_config.py
├── main.py                 # Application entry point
├── models.py               # Database models
├── routes.py               # URL routes and handlers
|__ run.py
├── websocket_handlers.py   # Real-time WebSocket handlers
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔑 API Keys Setup

### Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com)
2. Sign in with your Google account
3. Click "Get API Key"
4. Copy the key that starts with "AI"

### Hugging Face API Key (Optional)
1. Go to [Hugging Face](https://huggingface.co)
2. Create an account and go to Settings > Access Tokens
3. Create a new token with read permissions

## 🌟 Key Components

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite for development (PostgreSQL ready for production)
- **Authentication**: Secure session-based authentication
- **WebSocket Support**: Flask-SocketIO for real-time updates

### AI/ML Integration
- **Primary AI**: Google Gemini AI for health recommendations
- **Medical NLP**: Hugging Face models for medical entity extraction
- **Recommendation Engine**: Hybrid approach combining multiple algorithms

### Frontend
- **Template Engine**: Jinja2 with Flask
- **CSS Framework**: Bootstrap 5
- **JavaScript**: Vanilla JS with modular architecture
- **Real-time**: Socket.IO for live updates

## 🚀 Production Deployment

For production deployment:

1. Use PostgreSQL database
2. Set environment variables securely
3. Use a WSGI server like Gunicorn
4. Configure SSL/TLS
5. Set up proper logging and monitoring

## 📄 License

This project is for educational and demonstration purposes.
