import json
import logging
from flask import session
from flask_socketio import emit, join_room, leave_room, disconnect
from app import socketio, db
from ai_services import generate_health_recommendations, get_content_based_recommendations
from models import User, UserActivity
import datetime
logger = logging.getLogger(__name__)

def track_user_activity(user_id, activity_type, content_id=None, search_query=None, duration=None, metadata=None):
    """Track user activity for recommendation system"""
    try:
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            content_id=content_id,
            search_query=search_query,
            duration=duration,
            activity_metadata=json.dumps(metadata) if metadata else None
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error tracking activity: {e}")

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    user_id = session.get('user_id')
    if user_id:
        join_room(f'user_{user_id}')
        emit('status', {'msg': f'Connected to real-time updates'})
        logger.info(f"User {user_id} connected to WebSocket")
    else:
        disconnect()

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    user_id = session.get('user_id')
    if user_id:
        leave_room(f'user_{user_id}')
        logger.info(f"User {user_id} disconnected from WebSocket")

@socketio.on('request_recommendations')
def handle_recommendation_request(data):
    """Handle real-time recommendation requests"""
    user_id = session.get('user_id')
    if not user_id:
        emit('error', {'message': 'Not authenticated'})
        return

    try:
        # Track the request activity
        track_user_activity(user_id, 'recommendation_request', metadata=data)
        
        # Get AI-powered recommendations
        ai_recommendations = generate_health_recommendations(user_id)
        
        # Get content-based recommendations
        content_recommendations = get_content_based_recommendations(user_id, limit=5)
        
        # Format content recommendations
        content_recs = []
        for content in content_recommendations:
            content_recs.append({
                'id': content.id,
                'title': content.title,
                'category': content.category,
                'content_type': content.content_type,
                'description': content.description,
                'difficulty_level': content.difficulty_level,
                'duration': content.duration
            })
        
        # Emit recommendations back to client
        emit('recommendations_update', {
            'ai_recommendations': ai_recommendations,
            'content_recommendations': content_recs,
            'timestamp': str(UserActivity.query.filter_by(user_id=user_id).first().timestamp if UserActivity.query.filter_by(user_id=user_id).first() else "")
        })
        
    except Exception as e:
        logger.error(f"Error handling recommendation request: {e}")
        emit('error', {'message': 'Failed to generate recommendations'})

@socketio.on('track_activity')
def handle_activity_tracking(data):
    """Handle real-time activity tracking"""
    user_id = session.get('user_id')
    if not user_id:
        return

    try:
        activity_type = data.get('type')
        content_id = data.get('content_id')
        search_query = data.get('search_query')
        duration = data.get('duration')
        metadata = data.get('metadata')
        
        track_user_activity(user_id, activity_type, content_id, search_query, duration, metadata)
        
        # Send updated recommendations if this was a significant activity
        if activity_type in ['view', 'rating', 'bookmark']:
            content_recommendations = get_content_based_recommendations(user_id, limit=3)
            content_recs = []
            for content in content_recommendations:
                content_recs.append({
                    'id': content.id,
                    'title': content.title,
                    'category': content.category,
                    'content_type': content.content_type
                })
            
            emit('quick_recommendations', {'recommendations': content_recs})
            
    except Exception as e:
        logger.error(f"Error tracking activity: {e}")

@socketio.on('search_suggestions')
def handle_search_suggestions(data):
    """Handle real-time search suggestions"""
    user_id = session.get('user_id')
    query = data.get('query', '').lower()
    
    if len(query) < 2:
        emit('search_suggestions', {'suggestions': []})
        return
    
    try:
        # Track search activity
        if user_id:
            track_user_activity(user_id, 'search', search_query=query)
        
        # Get suggestions based on content titles and categories
        from models import HealthContent
        suggestions = []
        
        # Search in titles
        title_matches = HealthContent.query.filter(
            HealthContent.title.ilike(f'%{query}%')
        ).limit(5).all()
        
        for content in title_matches:
            suggestions.append({
                'text': content.title,
                'type': 'content',
                'category': content.category
            })
        
        # Search in categories
        category_matches = db.session.query(HealthContent.category.distinct())\
            .filter(HealthContent.category.ilike(f'%{query}%')).limit(3).all()
        
        for category in category_matches:
            suggestions.append({
                'text': category[0].replace('_', ' ').title(),
                'type': 'category',
                'category': category[0]
            })
        
        emit('search_suggestions', {'suggestions': suggestions[:8]})
        
    except Exception as e:
        logger.error(f"Error generating search suggestions: {e}")
        emit('search_suggestions', {'suggestions': []})

@socketio.on('health_check')
def handle_health_check():
    """Handle health check ping"""
    emit('health_response', {'status': 'healthy', 'timestamp': str(datetime.utcnow())})
