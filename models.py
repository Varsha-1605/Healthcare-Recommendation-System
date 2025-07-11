from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    medical_conditions = db.Column(db.Text, nullable=True)
    medications = db.Column(db.Text, nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String(100), nullable=True)
    
    # New fields for recommendation system
    preferred_content_types = db.Column(db.Text, nullable=True)  # JSON array
    fitness_level = db.Column(db.String(20), nullable=True)
    health_goals = db.Column(db.Text, nullable=True)
    notification_preferences = db.Column(db.Text, nullable=True)  # JSON
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    consultations = db.relationship('Consultation', backref='user', lazy=True)
    activities = db.relationship('UserActivity', backref='user', lazy=True)
    ratings = db.relationship('UserRating', backref='user', lazy=True)
    bookmarks = db.relationship('UserBookmark', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class HealthContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # 'article', 'video', 'exercise', 'treatment', 'diet'
    category = db.Column(db.String(100), nullable=False)  # 'cardiology', 'nutrition', 'fitness', 'mental_health'
    description = db.Column(db.Text, nullable=True)
    content_url = db.Column(db.String(500), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    tags = db.Column(db.Text, nullable=True)  # JSON array of tags
    difficulty_level = db.Column(db.String(20), nullable=True)  # 'beginner', 'intermediate', 'advanced'
    duration = db.Column(db.Integer, nullable=True)  # in minutes
    target_age_min = db.Column(db.Integer, nullable=True)
    target_age_max = db.Column(db.Integer, nullable=True)
    target_conditions = db.Column(db.Text, nullable=True)  # JSON array
    popularity_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ratings = db.relationship('UserRating', backref='content', lazy=True)
    activities = db.relationship('UserActivity', backref='content', lazy=True)
    bookmarks = db.relationship('UserBookmark', backref='content', lazy=True)

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 'view', 'search', 'click', 'rating', 'bookmark'
    content_id = db.Column(db.Integer, db.ForeignKey('health_content.id'), nullable=True)
    search_query = db.Column(db.String(200), nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # time spent in seconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    activity_metadata = db.Column(db.Text, nullable=True)  # JSON for additional context

class UserRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('health_content.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 scale
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserBookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('health_content.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    analysis_result = db.Column(db.Text, nullable=True)
    recommendations = db.Column(db.Text, nullable=True)
    extracted_entities = db.Column(db.Text, nullable=True)
    severity_level = db.Column(db.String(20), nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PredictiveInsight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    insight_type = db.Column(db.String(50), nullable=False)  # 'health_risk', 'wellness_trend', 'recommendation'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    priority_level = db.Column(db.String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('insights', lazy=True))
