# import json
# import logging
# from datetime import datetime, timedelta
# from functools import wraps

# from flask import render_template, request, redirect, url_for, flash, session, jsonify
# from werkzeug.security import generate_password_hash, check_password_hash

# from app import app, db, socketio
# from models import User, HealthContent, UserActivity, UserRating, UserBookmark, Consultation, PredictiveInsight
# from ai_services import (
#     extract_medical_entities, 
#     analyze_symptoms_with_gemini, 
#     generate_health_recommendations,
#     get_content_based_recommendations,
#     generate_predictive_insights
# )
# from websocket_handlers import track_user_activity

# logger = logging.getLogger(__name__)

# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             flash('Please log in to access this page.', 'error')
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#     return decorated_function

# def get_current_user():
#     """Helper function to get current user"""
#     user_id = session.get('user_id')
#     if user_id:
#         return User.query.get(user_id)
#     return None

# @app.route('/')
# def index():
#     """Homepage with featured content and recommendations"""
#     user = get_current_user()
    
#     # Get featured content
#     featured_content = HealthContent.query.order_by(
#         HealthContent.popularity_score.desc()
#     ).limit(6).all()
    
#     recommendations = []
#     if user:
#         # Get personalized recommendations
#         recommendations = get_content_based_recommendations(user.id, limit=4)
        
#         # Track homepage visit
#         track_user_activity(user.id, 'homepage_visit')
    
#     return render_template('index.html', 
#                          user=user, 
#                          featured_content=featured_content,
#                          recommendations=recommendations)

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     """User registration"""
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']
#         full_name = request.form['full_name']
#         age = int(request.form['age'])
#         gender = request.form['gender']
#         phone = request.form.get('phone', '')
#         medical_conditions = request.form.get('medical_conditions', '')
#         medications = request.form.get('medications', '')
#         allergies = request.form.get('allergies', '')
#         fitness_level = request.form.get('fitness_level', 'beginner')
#         health_goals = request.form.get('health_goals', '')
        
#         # Check if user already exists
#         if User.query.filter_by(username=username).first():
#             flash('Username already exists', 'error')
#             return render_template('register.html')
        
#         if User.query.filter_by(email=email).first():
#             flash('Email already registered', 'error')
#             return render_template('register.html')
        
#         # Create new user
#         user = User(
#             username=username,
#             email=email,
#             full_name=full_name,
#             age=age,
#             gender=gender,
#             phone=phone,
#             medical_conditions=medical_conditions,
#             medications=medications,
#             allergies=allergies,
#             fitness_level=fitness_level,
#             health_goals=health_goals
#         )
#         user.set_password(password)
        
#         db.session.add(user)
#         db.session.commit()
        
#         flash('Registration successful! Please log in.', 'success')
#         return redirect(url_for('login'))
    
#     return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     """User login"""
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         user = User.query.filter_by(username=username).first()
        
#         if user and user.check_password(password):
#             session['user_id'] = user.id
#             session['username'] = user.username
#             flash('Login successful!', 'success')
            
#             # Track login activity
#             track_user_activity(user.id, 'login')
            
#             next_page = request.args.get('next')
#             return redirect(next_page) if next_page else redirect(url_for('dashboard'))
#         else:
#             flash('Invalid username or password', 'error')
    
#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     """User logout"""
#     user_id = session.get('user_id')
#     if user_id:
#         track_user_activity(user_id, 'logout')
    
#     session.clear()
#     flash('You have been logged out', 'info')
#     return redirect(url_for('index'))

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     """User dashboard with personalized content"""
#     user = get_current_user()
    
#     # Get recent activity
#     recent_activities = UserActivity.query.filter_by(user_id=user.id)\
#         .order_by(UserActivity.timestamp.desc()).limit(10).all()
    
#     # Get bookmarked content
#     bookmarks = UserBookmark.query.filter_by(user_id=user.id)\
#         .order_by(UserBookmark.created_at.desc()).limit(5).all()
    
#     # Get personalized recommendations
#     recommendations = get_content_based_recommendations(user.id, limit=6)
    
#     # Get recent consultations
#     consultations = Consultation.query.filter_by(user_id=user.id)\
#         .order_by(Consultation.created_at.desc()).limit(3).all()
    
#     # Get predictive insights
#     insights = PredictiveInsight.query.filter_by(user_id=user.id, is_active=True)\
#         .order_by(PredictiveInsight.created_at.desc()).limit(4).all()
    
#     # Track dashboard visit
#     track_user_activity(user.id, 'dashboard_visit')
    
#     return render_template('dashboard.html',
#                          user=user,
#                          recent_activities=recent_activities,
#                          bookmarks=bookmarks,
#                          recommendations=recommendations,
#                          consultations=consultations,
#                          insights=insights)

# @app.route('/profile', methods=['GET', 'POST'])
# @login_required
# def profile():
#     """User profile management"""
#     user = get_current_user()
    
#     if request.method == 'POST':
#         user.full_name = request.form['full_name']
#         user.email = request.form['email']
#         user.age = int(request.form['age'])
#         user.gender = request.form['gender']
#         user.phone = request.form.get('phone', '')
#         user.medical_conditions = request.form.get('medical_conditions', '')
#         user.medications = request.form.get('medications', '')
#         user.allergies = request.form.get('allergies', '')
#         user.fitness_level = request.form.get('fitness_level', 'beginner')
#         user.health_goals = request.form.get('health_goals', '')
        
#         db.session.commit()
#         flash('Profile updated successfully!', 'success')
        
#         # Track profile update
#         track_user_activity(user.id, 'profile_update')
        
#         return redirect(url_for('profile'))
    
#     return render_template('profile.html', user=user)

# @app.route('/consultation', methods=['GET', 'POST'])
# @login_required
# def consultation():
#     """AI-powered health consultation"""
#     user = get_current_user()
    
#     if request.method == 'POST':
#         symptoms = request.form['symptoms']
        
#         # Extract medical entities
#         entities = extract_medical_entities(symptoms)
        
#         # Analyze symptoms with Gemini AI
#         user_profile = {
#             'age': user.age,
#             'gender': user.gender,
#             'medical_conditions': user.medical_conditions,
#             'medications': user.medications,
#             'allergies': user.allergies
#         }
        
#         analysis = analyze_symptoms_with_gemini(symptoms, user_profile)
        
#         # Save consultation
#         consultation = Consultation(
#             user_id=user.id,
#             symptoms=symptoms,
#             analysis_result=json.dumps(analysis),
#             extracted_entities=json.dumps(entities),
#             severity_level=analysis.get('severity', 'unknown'),
#             confidence_score=analysis.get('confidence', 0.0)
#         )
        
#         db.session.add(consultation)
#         db.session.commit()
        
#         # Track consultation activity
#         track_user_activity(user.id, 'consultation', metadata={'consultation_id': consultation.id})
        
#         flash('Consultation completed. Please review the analysis below.', 'info')
#         return render_template('consultation.html', 
#                              consultation=consultation, 
#                              analysis=analysis, 
#                              entities=entities)
    
#     return render_template('consultation.html')

# @app.route('/consultation_history')
# @login_required
# def consultation_history():
#     """View consultation history"""
#     user = get_current_user()
    
#     consultations = Consultation.query.filter_by(user_id=user.id)\
#         .order_by(Consultation.created_at.desc()).all()
    
#     # Track consultation history view
#     track_user_activity(user.id, 'consultation_history_view')
    
#     return render_template('consultation_history.html', consultations=consultations)

# @app.route('/consultation/<int:consultation_id>')
# @login_required
# def view_consultation(consultation_id):
#     """View specific consultation"""
#     user = get_current_user()
#     consultation = Consultation.query.filter_by(id=consultation_id, user_id=user.id).first_or_404()
    
#     analysis = json.loads(consultation.analysis_result) if consultation.analysis_result else {}
#     entities = json.loads(consultation.extracted_entities) if consultation.extracted_entities else []
    
#     # Track consultation view
#     track_user_activity(user.id, 'consultation_view', metadata={'consultation_id': consultation_id})
    
#     return render_template('consultation.html', 
#                          consultation=consultation, 
#                          analysis=analysis, 
#                          entities=entities)

# @app.route('/content/<int:content_id>')
# def content_detail(content_id):
#     """View specific health content"""
#     content = HealthContent.query.get_or_404(content_id)
#     user = get_current_user()
    
#     user_rating = None
#     is_bookmarked = False
    
#     if user:
#         user_rating = UserRating.query.filter_by(user_id=user.id, content_id=content_id).first()
#         is_bookmarked = UserBookmark.query.filter_by(user_id=user.id, content_id=content_id).first() is not None
        
#         # Track content view
#         track_user_activity(user.id, 'view', content_id=content_id)
    
#     # Get related content
#     related_content = HealthContent.query.filter(
#         HealthContent.category == content.category,
#         HealthContent.id != content_id
#     ).limit(4).all()
    
#     return render_template('content_detail.html',
#                          content=content,
#                          user=user,
#                          user_rating=user_rating,
#                          is_bookmarked=is_bookmarked,
#                          related_content=related_content)

# @app.route('/search')
# def search():
#     """Search health content"""
#     query = request.args.get('q', '')
#     category = request.args.get('category', '')
#     content_type = request.args.get('type', '')
    
#     user = get_current_user()
    
#     # Build search query
#     search_query = HealthContent.query
    
#     if query:
#         search_query = search_query.filter(
#             db.or_(
#                 HealthContent.title.ilike(f'%{query}%'),
#                 HealthContent.description.ilike(f'%{query}%')
#             )
#         )
    
#     if category:
#         search_query = search_query.filter(HealthContent.category == category)
    
#     if content_type:
#         search_query = search_query.filter(HealthContent.content_type == content_type)
    
#     results = search_query.order_by(HealthContent.popularity_score.desc()).all()
    
#     # Get all categories for filter
#     categories = db.session.query(HealthContent.category.distinct()).all()
#     content_types = db.session.query(HealthContent.content_type.distinct()).all()
    
#     if user and query:
#         # Track search activity
#         track_user_activity(user.id, 'search', search_query=query)
    
#     return render_template('search.html',
#                          results=results,
#                          query=query,
#                          category=category,
#                          content_type=content_type,
#                          categories=[c[0] for c in categories],
#                          content_types=[c[0] for c in content_types])

# @app.route('/analytics')
# @login_required
# def analytics():
#     """Advanced analytics dashboard"""
#     user = get_current_user()
    
#     # Generate fresh predictive insights
#     insights = generate_predictive_insights(user.id)
    
#     # Get activity statistics
#     activity_stats = db.session.query(
#         UserActivity.activity_type,
#         db.func.count(UserActivity.id).label('count')
#     ).filter_by(user_id=user.id).group_by(UserActivity.activity_type).all()
    
#     # Get consultation trends
#     consultation_trends = db.session.query(
#         db.func.date(Consultation.created_at).label('date'),
#         db.func.count(Consultation.id).label('count')
#     ).filter_by(user_id=user.id)\
#      .filter(Consultation.created_at > datetime.utcnow() - timedelta(days=30))\
#      .group_by(db.func.date(Consultation.created_at)).all()
    
#     # Get category preferences
#     category_stats = db.session.query(
#         HealthContent.category,
#         db.func.count(UserActivity.id).label('views')
#     ).join(UserActivity, UserActivity.content_id == HealthContent.id)\
#      .filter(UserActivity.user_id == user.id)\
#      .group_by(HealthContent.category).all()
    
#     # Track analytics view
#     track_user_activity(user.id, 'analytics_view')
    
#     return render_template('analytics.html',
#                          user=user,
#                          insights=insights,
#                          activity_stats=activity_stats,
#                          consultation_trends=consultation_trends,
#                          category_stats=category_stats)

# # API Endpoints
# @app.route('/api/rate_content', methods=['POST'])
# @login_required
# def rate_content():
#     """Rate health content"""
#     user = get_current_user()
#     content_id = request.form.get('content_id', type=int)
#     rating = request.form.get('rating', type=int)
#     review = request.form.get('review', '')
    
#     if not content_id or not rating or rating < 1 or rating > 5:
#         return jsonify({'error': 'Invalid rating data'}), 400
    
#     # Check if user already rated this content
#     existing_rating = UserRating.query.filter_by(user_id=user.id, content_id=content_id).first()
    
#     if existing_rating:
#         existing_rating.rating = rating
#         existing_rating.review = review
#     else:
#         new_rating = UserRating(
#             user_id=user.id,
#             content_id=content_id,
#             rating=rating,
#             review=review
#         )
#         db.session.add(new_rating)
    
#     db.session.commit()
    
#     # Track rating activity
#     track_user_activity(user.id, 'rating', content_id=content_id, metadata={'rating': rating})
    
#     return jsonify({'success': True, 'message': 'Rating saved successfully'})

# @app.route('/api/bookmark_content', methods=['POST'])
# @login_required
# def bookmark_content():
#     """Bookmark/unbookmark health content"""
#     user = get_current_user()
#     content_id = request.form.get('content_id', type=int)
    
#     if not content_id:
#         return jsonify({'error': 'Invalid content ID'}), 400
    
#     # Check if already bookmarked
#     existing_bookmark = UserBookmark.query.filter_by(user_id=user.id, content_id=content_id).first()
    
#     if existing_bookmark:
#         db.session.delete(existing_bookmark)
#         action = 'removed'
#     else:
#         new_bookmark = UserBookmark(user_id=user.id, content_id=content_id)
#         db.session.add(new_bookmark)
#         action = 'added'
    
#     db.session.commit()
    
#     # Track bookmark activity
#     track_user_activity(user.id, 'bookmark', content_id=content_id, metadata={'action': action})
    
#     return jsonify({'success': True, 'action': action})

# @app.route('/api/recommendations/refresh')
# @login_required
# def refresh_recommendations():
#     """Get fresh AI recommendations"""
#     user = get_current_user()
    
#     # Get AI-powered recommendations
#     ai_recommendations = generate_health_recommendations(user.id)
    
#     # Get content-based recommendations
#     content_recommendations = get_content_based_recommendations(user.id, limit=6)
    
#     content_recs = []
#     for content in content_recommendations:
#         content_recs.append({
#             'id': content.id,
#             'title': content.title,
#             'category': content.category,
#             'content_type': content.content_type,
#             'description': content.description,
#             'url': url_for('content_detail', content_id=content.id)
#         })
    
#     # Track recommendation request
#     track_user_activity(user.id, 'recommendation_request')
    
#     return jsonify({
#         'ai_recommendations': ai_recommendations,
#         'content_recommendations': content_recs
#     })

# @app.route('/api/content/categories')
# def get_categories():
#     """Get all content categories"""
#     categories = db.session.query(HealthContent.category.distinct()).all()
#     return jsonify([c[0] for c in categories])

# # Error handlers
# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('404.html'), 404

# @app.errorhandler(500)
# def internal_error(error):
#     db.session.rollback()
#     return render_template('500.html'), 500
























































































import json
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db, socketio
from models import User, HealthContent, UserActivity, UserRating, UserBookmark, Consultation, PredictiveInsight
from ai_services import (
    extract_medical_entities, 
    analyze_symptoms_with_gemini, 
    generate_health_recommendations,
    get_content_based_recommendations,
    generate_predictive_insights
)
from websocket_handlers import track_user_activity

logger = logging.getLogger(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Helper function to get current user"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

@app.route('/')
def index():
    """Homepage with featured content and recommendations"""
    user = get_current_user()
    
    # Get featured content
    featured_content = HealthContent.query.order_by(
        HealthContent.popularity_score.desc()
    ).limit(6).all()
    
    recommendations = []
    if user:
        # Get personalized recommendations
        recommendations = get_content_based_recommendations(user.id, limit=4)
        
        # Track homepage visit
        track_user_activity(user.id, 'homepage_visit')
    
    return render_template('index.html', 
                         user=user, 
                         featured_content=featured_content,
                         recommendations=recommendations)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        age = int(request.form['age'])
        gender = request.form['gender']
        phone = request.form.get('phone', '')
        medical_conditions = request.form.get('medical_conditions', '')
        medications = request.form.get('medications', '')
        allergies = request.form.get('allergies', '')
        fitness_level = request.form.get('fitness_level', 'beginner')
        health_goals = request.form.get('health_goals', '')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            age=age,
            gender=gender,
            phone=phone,
            medical_conditions=medical_conditions,
            medications=medications,
            allergies=allergies,
            fitness_level=fitness_level,
            health_goals=health_goals
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            
            # Track login activity
            track_user_activity(user.id, 'login')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    user_id = session.get('user_id')
    if user_id:
        track_user_activity(user_id, 'logout')
    
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with personalized content"""
    user = get_current_user()
    
    # Get recent activity
    recent_activities = UserActivity.query.filter_by(user_id=user.id)\
        .order_by(UserActivity.timestamp.desc()).limit(10).all()
    
    # Get bookmarked content
    bookmarks = UserBookmark.query.filter_by(user_id=user.id)\
        .order_by(UserBookmark.created_at.desc()).limit(5).all()
    
    # Get personalized recommendations
    recommendations = get_content_based_recommendations(user.id, limit=6)
    
    # Get recent consultations
    consultations = Consultation.query.filter_by(user_id=user.id)\
        .order_by(Consultation.created_at.desc()).limit(3).all()
    
    # Get predictive insights
    insights = PredictiveInsight.query.filter_by(user_id=user.id, is_active=True)\
        .order_by(PredictiveInsight.created_at.desc()).limit(4).all()
    
    # Track dashboard visit
    track_user_activity(user.id, 'dashboard_visit')
    
    return render_template('dashboard.html',
                         user=user,
                         recent_activities=recent_activities,
                         bookmarks=bookmarks,
                         recommendations=recommendations,
                         consultations=consultations,
                         insights=insights)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    user = get_current_user()
    
    if request.method == 'POST':
        user.full_name = request.form['full_name']
        user.email = request.form['email']
        user.age = int(request.form['age'])
        user.gender = request.form['gender']
        user.phone = request.form.get('phone', '')
        user.medical_conditions = request.form.get('medical_conditions', '')
        user.medications = request.form.get('medications', '')
        user.allergies = request.form.get('allergies', '')
        user.fitness_level = request.form.get('fitness_level', 'beginner')
        user.health_goals = request.form.get('health_goals', '')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
        # Track profile update
        track_user_activity(user.id, 'profile_update')
        
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=user)

@app.route('/consultation', methods=['GET', 'POST'])
@login_required
def consultation():
    """AI-powered health consultation"""
    user = get_current_user()
    
    if request.method == 'POST':
        symptoms = request.form['symptoms']
        
        # Extract medical entities
        entities = extract_medical_entities(symptoms)
        
        # Analyze symptoms with Gemini AI
        user_profile = {
            'age': user.age,
            'gender': user.gender,
            'medical_conditions': user.medical_conditions,
            'medications': user.medications,
            'allergies': user.allergies
        }
        
        analysis = analyze_symptoms_with_gemini(symptoms, user_profile)
        
        # Save consultation
        consultation = Consultation(
            user_id=user.id,
            symptoms=symptoms,
            analysis_result=json.dumps(analysis),
            extracted_entities=json.dumps(entities),
            severity_level=analysis.get('severity', 'unknown'),
            confidence_score=analysis.get('confidence', 0.0)
        )
        
        db.session.add(consultation)
        db.session.commit()
        
        # Track consultation activity
        track_user_activity(user.id, 'consultation', metadata={'consultation_id': consultation.id})
        
        flash('Consultation completed. Please review the analysis below.', 'info')
        return render_template('consultation.html', 
                             consultation=consultation, 
                             analysis=analysis, 
                             entities=entities)
    
    return render_template('consultation.html')

@app.route('/consultation_history')
@login_required
def consultation_history():
    """View consultation history"""
    user = get_current_user()
    
    consultations = Consultation.query.filter_by(user_id=user.id)\
        .order_by(Consultation.created_at.desc()).all()
    
    # Track consultation history view
    track_user_activity(user.id, 'consultation_history_view')
    
    return render_template('consultation_history.html', consultations=consultations)

@app.route('/consultation/<int:consultation_id>')
@login_required
def view_consultation(consultation_id):
    """View specific consultation"""
    user = get_current_user()
    consultation = Consultation.query.filter_by(id=consultation_id, user_id=user.id).first_or_404()
    
    analysis = json.loads(consultation.analysis_result) if consultation.analysis_result else {}
    entities = json.loads(consultation.extracted_entities) if consultation.extracted_entities else []
    
    # Track consultation view
    track_user_activity(user.id, 'consultation_view', metadata={'consultation_id': consultation_id})
    
    return render_template('consultation.html', 
                         consultation=consultation, 
                         analysis=analysis, 
                         entities=entities)

@app.route('/content/<int:content_id>')
def content_detail(content_id):
    """View specific health content"""
    content = HealthContent.query.get_or_404(content_id)
    user = get_current_user()
    
    user_rating = None
    is_bookmarked = False
    
    if user:
        user_rating = UserRating.query.filter_by(user_id=user.id, content_id=content_id).first()
        is_bookmarked = UserBookmark.query.filter_by(user_id=user.id, content_id=content_id).first() is not None
        
        # Track content view
        track_user_activity(user.id, 'view', content_id=content_id)
    
    # Get related content
    related_content = HealthContent.query.filter(
        HealthContent.category == content.category,
        HealthContent.id != content_id
    ).limit(4).all()
    
    return render_template('content_detail.html',
                         content=content,
                         user=user,
                         user_rating=user_rating,
                         is_bookmarked=is_bookmarked,
                         related_content=related_content)

@app.route('/search')
def search():
    """Search health content"""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    content_type = request.args.get('type', '')
    
    user = get_current_user()
    
    # Build search query
    search_query = HealthContent.query
    
    if query:
        search_query = search_query.filter(
            db.or_(
                HealthContent.title.ilike(f'%{query}%'),
                HealthContent.description.ilike(f'%{query}%')
            )
        )
    
    if category:
        search_query = search_query.filter(HealthContent.category == category)
    
    if content_type:
        search_query = search_query.filter(HealthContent.content_type == content_type)
    
    results = search_query.order_by(HealthContent.popularity_score.desc()).all()
    
    # Get all categories for filter
    categories = db.session.query(HealthContent.category.distinct()).all()
    content_types = db.session.query(HealthContent.content_type.distinct()).all()
    
    if user and query:
        # Track search activity
        track_user_activity(user.id, 'search', search_query=query)
    
    return render_template('search.html',
                         results=results,
                         query=query,
                         category=category,
                         content_type=content_type,
                         categories=[c[0] for c in categories],
                         content_types=[c[0] for c in content_types])




@app.route('/analytics')
@login_required
def analytics():
    """Advanced analytics dashboard"""
    user = get_current_user()
    
    # Generate fresh predictive insights
    insights = generate_predictive_insights(user.id)
    
    # Get activity statistics
    activity_stats = db.session.query(
        UserActivity.activity_type,
        db.func.count(UserActivity.id).label('count')
    ).filter_by(user_id=user.id).group_by(UserActivity.activity_type).all()
    
    # Get consultation trends
    consultation_trends = db.session.query(
        db.func.date(Consultation.created_at).label('date'),
        db.func.count(Consultation.id).label('count')
    ).filter_by(user_id=user.id)\
     .filter(Consultation.created_at > datetime.utcnow() - timedelta(days=30))\
     .group_by(db.func.date(Consultation.created_at)).all()
    
    # Get category preferences
    category_stats = db.session.query(
        HealthContent.category,
        db.func.count(UserActivity.id).label('views')
    ).join(UserActivity, UserActivity.content_id == HealthContent.id)\
     .filter(UserActivity.user_id == user.id)\
     .group_by(HealthContent.category).all()
    
    # Track analytics view
    track_user_activity(user.id, 'analytics_view')
    
    return render_template('analytics.html',
                         user=user,
                         insights=insights,
                         activity_stats=activity_stats,
                         consultation_trends=consultation_trends,
                         category_stats=category_stats)

@app.route('/api/generate_insights')
@login_required
def generate_insights_api():
    """API endpoint to generate fresh insights"""
    user = get_current_user()
    
    try:
        # Generate fresh insights
        insights = generate_predictive_insights(user.id)
        
        # Also create some sample insights if none generated
        if not insights:
            from populate_data import add_sample_insights
            add_sample_insights(user.id)
            
            # Get the insights we just created
            db_insights = PredictiveInsight.query.filter_by(user_id=user.id, is_active=True).all()
            insights = []
            for insight in db_insights:
                insights.append({
                    'insight_type': insight.insight_type,
                    'title': insight.title,
                    'description': insight.description,
                    'confidence_score': insight.confidence_score,
                    'priority_level': insight.priority_level
                })
        
        track_user_activity(user.id, 'insights_generated')
        
        return jsonify({
            'success': True,
            'insights': insights
        })
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate insights'
        })

# API Endpoints
@app.route('/api/rate_content', methods=['POST'])
@login_required
def rate_content():
    """Rate health content"""
    user = get_current_user()
    content_id = request.form.get('content_id', type=int)
    rating = request.form.get('rating', type=int)
    review = request.form.get('review', '')
    
    if not content_id or not rating or rating < 1 or rating > 5:
        return jsonify({'error': 'Invalid rating data'}), 400
    
    # Check if user already rated this content
    existing_rating = UserRating.query.filter_by(user_id=user.id, content_id=content_id).first()
    
    if existing_rating:
        existing_rating.rating = rating
        existing_rating.review = review
    else:
        new_rating = UserRating(
            user_id=user.id,
            content_id=content_id,
            rating=rating,
            review=review
        )
        db.session.add(new_rating)
    
    db.session.commit()
    
    # Track rating activity
    track_user_activity(user.id, 'rating', content_id=content_id, metadata={'rating': rating})
    
    return jsonify({'success': True, 'message': 'Rating saved successfully'})

@app.route('/api/bookmark_content', methods=['POST'])
@login_required
def bookmark_content():
    """Bookmark/unbookmark health content"""
    user = get_current_user()
    content_id = request.form.get('content_id', type=int)
    
    if not content_id:
        return jsonify({'error': 'Invalid content ID'}), 400
    
    # Check if already bookmarked
    existing_bookmark = UserBookmark.query.filter_by(user_id=user.id, content_id=content_id).first()
    
    if existing_bookmark:
        db.session.delete(existing_bookmark)
        action = 'removed'
    else:
        new_bookmark = UserBookmark(user_id=user.id, content_id=content_id)
        db.session.add(new_bookmark)
        action = 'added'
    
    db.session.commit()
    
    # Track bookmark activity
    track_user_activity(user.id, 'bookmark', content_id=content_id, metadata={'action': action})
    
    return jsonify({'success': True, 'action': action})

@app.route('/api/recommendations/refresh')
@login_required
def refresh_recommendations():
    """Get fresh AI recommendations"""
    user = get_current_user()
    
    # Get AI-powered recommendations
    ai_recommendations = generate_health_recommendations(user.id)
    
    # Get content-based recommendations
    content_recommendations = get_content_based_recommendations(user.id, limit=6)
    
    content_recs = []
    for content in content_recommendations:
        content_recs.append({
            'id': content.id,
            'title': content.title,
            'category': content.category,
            'content_type': content.content_type,
            'description': content.description,
            'url': url_for('content_detail', content_id=content.id)
        })
    
    # Track recommendation request
    track_user_activity(user.id, 'recommendation_request')
    
    return jsonify({
        'ai_recommendations': ai_recommendations,
        'content_recommendations': content_recs
    })

@app.route('/api/content/categories')
def get_categories():
    """Get all content categories"""
    categories = db.session.query(HealthContent.category.distinct()).all()
    return jsonify([c[0] for c in categories])

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
