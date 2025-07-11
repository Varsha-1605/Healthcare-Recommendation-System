import json
import logging
import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import random

from google import genai
from google.genai import types
from pydantic import BaseModel

from app import db, HF_HEADERS, HF_API_BASE, BIOMEDICAL_NER_MODEL, MEDICAL_QA_MODEL, CLINICAL_CLASSIFIER_MODEL
from models import User, HealthContent, UserActivity, UserRating, UserBookmark, Consultation, PredictiveInsight

logger = logging.getLogger(__name__)

# Initialize Gemini AI
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'gemini_default_key')
client = genai.Client(api_key=GEMINI_API_KEY)

class HealthRecommendation(BaseModel):
    title: str
    description: str
    category: str
    priority: str
    confidence: float

class SymptomAnalysis(BaseModel):
    condition: str
    severity: str
    confidence: float
    recommendations: list

def extract_medical_entities(text):
    """Extract medical entities using Hugging Face NER model"""
    try:
        url = f"{HF_API_BASE}/{BIOMEDICAL_NER_MODEL}"
        response = requests.post(url, headers=HF_HEADERS, json={"inputs": text})
        
        if response.status_code == 200:
            entities = response.json()
            # Process and format entities
            processed_entities = []
            for entity in entities:
                if isinstance(entity, dict) and 'entity' in entity:
                    processed_entities.append({
                        'text': entity.get('word', ''),
                        'label': entity.get('entity', ''),
                        'confidence': entity.get('score', 0.0)
                    })
            return processed_entities
        else:
            logger.error(f"NER API error: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error extracting medical entities: {e}")
        return []

def answer_medical_question(question, context=""):
    """Answer medical questions using Hugging Face QA model"""
    try:
        url = f"{HF_API_BASE}/{MEDICAL_QA_MODEL}"
        payload = {
            "inputs": {
                "question": question,
                "context": context if context else "Medical and healthcare information context."
            }
        }
        response = requests.post(url, headers=HF_HEADERS, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict) and 'answer' in result:
                return result['answer']
        return "I'm unable to provide a specific answer at this time. Please consult with a healthcare professional."
    except Exception as e:
        logger.error(f"Error answering medical question: {e}")
        return "I'm unable to provide a specific answer at this time. Please consult with a healthcare professional."

def classify_medical_content(text):
    """Classify medical content using Hugging Face classification model"""
    try:
        url = f"{HF_API_BASE}/{CLINICAL_CLASSIFIER_MODEL}"
        response = requests.post(url, headers=HF_HEADERS, json={"inputs": text})
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0]
        return {"label": "general", "score": 0.5}
    except Exception as e:
        logger.error(f"Error classifying medical content: {e}")
        return {"label": "general", "score": 0.5}

def analyze_symptoms_with_gemini(symptoms_text, user_profile=None):
    """Analyze symptoms using Gemini AI"""
    try:
        profile_context = ""
        if user_profile:
            profile_context = f"""
            Patient Profile:
            - Age: {user_profile.get('age', 'unknown')}
            - Gender: {user_profile.get('gender', 'unknown')}
            - Medical Conditions: {user_profile.get('medical_conditions', 'none')}
            - Medications: {user_profile.get('medications', 'none')}
            - Allergies: {user_profile.get('allergies', 'none')}
            """

        system_prompt = """You are a medical AI assistant. Analyze the provided symptoms and provide a structured assessment. 
        IMPORTANT: Always include medical disclaimers and recommend consulting healthcare professionals.
        Provide your response in JSON format with: condition, severity, confidence, and recommendations."""

        prompt = f"""
        {profile_context}
        
        Symptoms: {symptoms_text}
        
        Please analyze these symptoms and provide:
        1. Most likely condition or conditions
        2. Severity level (low, moderate, high, critical)
        3. Confidence level (0.0 to 1.0)
        4. Recommendations for next steps
        
        Include appropriate medical disclaimers.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=SymptomAnalysis,
            ),
        )

        if response.text:
            analysis = json.loads(response.text)
            return analysis
        else:
            return {
                "condition": "Unable to analyze",
                "severity": "unknown",
                "confidence": 0.0,
                "recommendations": ["Please consult with a healthcare professional for proper diagnosis."]
            }

    except Exception as e:
        logger.error(f"Error analyzing symptoms with Gemini: {e}")
        return {
            "condition": "Analysis unavailable",
            "severity": "unknown", 
            "confidence": 0.0,
            "recommendations": ["Please consult with a healthcare professional for proper diagnosis."]
        }

def generate_health_recommendations(user_id):
    """Generate personalized health recommendations using Gemini AI"""
    try:
        user = User.query.get(user_id)
        if not user:
            return []

        user_profile = {
            'age': user.age,
            'gender': user.gender,
            'medical_conditions': user.medical_conditions,
            'medications': user.medications,
            'fitness_level': user.fitness_level,
            'health_goals': user.health_goals
        }

        # Get user's recent activity patterns
        recent_activities = UserActivity.query.filter_by(user_id=user_id)\
            .filter(UserActivity.timestamp > datetime.utcnow() - timedelta(days=30))\
            .all()

        activity_summary = defaultdict(int)
        for activity in recent_activities:
            if activity.content_id:
                content = HealthContent.query.get(activity.content_id)
                if content:
                    activity_summary[content.category] += 1

        system_prompt = """You are a healthcare AI assistant specializing in personalized health recommendations. 
        Generate specific, actionable health recommendations based on the user profile and activity patterns.
        Provide recommendations in JSON format with title, description, category, priority, and confidence."""

        prompt = f"""
        User Profile: {json.dumps(user_profile)}
        Recent Activity: {dict(activity_summary)}
        
        Generate 3-5 personalized health recommendations that are:
        1. Specific to the user's profile and conditions
        2. Actionable and practical
        3. Evidence-based when possible
        4. Include appropriate medical disclaimers
        
        Categories: nutrition, fitness, mental_health, cardiology, preventive_care, lifestyle
        Priority levels: low, medium, high
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
            ),
        )

        if response.text:
            recommendations_data = json.loads(response.text)
            if isinstance(recommendations_data, list):
                return recommendations_data
            elif isinstance(recommendations_data, dict) and 'recommendations' in recommendations_data:
                return recommendations_data['recommendations']
        
        return []

    except Exception as e:
        logger.error(f"Error generating health recommendations: {e}")
        return []

def get_content_based_recommendations(user_id, limit=10):
    """Content-based filtering recommendations"""
    user = User.query.get(user_id)
    if not user:
        return []

    interests = get_user_interests(user_id)
    
    # Build query based on user interests
    query = HealthContent.query
    
    # Filter by categories if user has interests
    if interests.get('categories'):
        query = query.filter(HealthContent.category.in_(interests['categories']))
    
    # Filter by age range
    if user.age:
        query = query.filter(
            db.or_(
                HealthContent.target_age_min == None,
                HealthContent.target_age_min <= user.age
            ),
            db.or_(
                HealthContent.target_age_max == None,
                HealthContent.target_age_max >= user.age
            )
        )
    
    # Exclude already viewed content
    viewed_content_ids = db.session.query(UserActivity.content_id)\
        .filter_by(user_id=user_id, activity_type='view')\
        .filter(UserActivity.content_id.isnot(None))\
        .subquery()
    
    query = query.filter(~HealthContent.id.in_(viewed_content_ids))
    
    # Order by popularity and creation date
    recommendations = query.order_by(
        HealthContent.popularity_score.desc(),
        HealthContent.created_at.desc()
    ).limit(limit).all()
    
    return recommendations

def get_user_interests(user_id):
    """Extract user interests from profile and activity history"""
    user = User.query.get(user_id)
    if not user:
        return {}

    interests = {
        'categories': [],
        'content_types': [],
        'conditions': [],
        'age_group': None,
        'fitness_level': user.fitness_level or 'beginner'
    }
    
    # Extract from medical conditions
    if user.medical_conditions:
        conditions = user.medical_conditions.lower()
        if 'diabetes' in conditions:
            interests['categories'].append('endocrinology')
        if 'heart' in conditions or 'cardiac' in conditions:
            interests['categories'].append('cardiology')
        if 'mental' in conditions or 'anxiety' in conditions or 'depression' in conditions:
            interests['categories'].append('mental_health')
        if 'weight' in conditions or 'obesity' in conditions:
            interests['categories'].append('nutrition')
    
    # Extract from user activity
    recent_activities = UserActivity.query.filter_by(user_id=user_id)\
        .filter(UserActivity.timestamp > datetime.utcnow() - timedelta(days=30))\
        .all()
    
    activity_categories = defaultdict(int)
    activity_types = defaultdict(int)
    
    for activity in recent_activities:
        if activity.content_id:
            content = HealthContent.query.get(activity.content_id)
            if content:
                activity_categories[content.category] += 1
                activity_types[content.content_type] += 1
    
    # Get top categories and content types
    interests['categories'].extend([cat for cat, count in 
                                  sorted(activity_categories.items(), key=lambda x: x[1], reverse=True)[:3]])
    interests['content_types'].extend([ctype for ctype, count in 
                                     sorted(activity_types.items(), key=lambda x: x[1], reverse=True)[:3]])
    
    # Age group
    if user.age < 30:
        interests['age_group'] = 'young_adult'
    elif user.age < 50:
        interests['age_group'] = 'adult'
    elif user.age < 65:
        interests['age_group'] = 'middle_aged'
    else:
        interests['age_group'] = 'senior'
    
    return interests

def generate_predictive_insights(user_id):
    """Generate predictive health insights using AI analysis"""
    try:
        user = User.query.get(user_id)
        if not user:
            return []

        # Gather user data for analysis
        recent_activities = UserActivity.query.filter_by(user_id=user_id)\
            .filter(UserActivity.timestamp > datetime.utcnow() - timedelta(days=90))\
            .all()

        consultations = Consultation.query.filter_by(user_id=user_id)\
            .order_by(Consultation.created_at.desc())\
            .limit(5).all()

        user_data = {
            'profile': {
                'age': user.age,
                'gender': user.gender,
                'medical_conditions': user.medical_conditions,
                'medications': user.medications,
                'fitness_level': user.fitness_level
            },
            'activity_patterns': len(recent_activities),
            'consultation_history': [c.symptoms for c in consultations]
        }

        system_prompt = """You are a healthcare analytics AI. Generate predictive health insights based on user data patterns.
        Focus on wellness trends, potential health risks, and preventive recommendations.
        Provide insights in JSON format with type, title, description, confidence, and priority."""

        prompt = f"""
        User Data: {json.dumps(user_data)}
        
        Generate 2-4 predictive health insights focusing on:
        1. Wellness trends and patterns
        2. Potential health risks to monitor
        3. Preventive care recommendations
        4. Lifestyle optimization suggestions
        
        Insight types: health_risk, wellness_trend, preventive_care, lifestyle_optimization
        Priority levels: low, medium, high, critical
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if response.text:
            # Parse and save insights to database
            insights_data = json.loads(response.text)
            saved_insights = []
            
            for insight_data in insights_data:
                insight = PredictiveInsight(
                    user_id=user_id,
                    insight_type=insight_data.get('type', 'wellness_trend'),
                    title=insight_data.get('title', ''),
                    description=insight_data.get('description', ''),
                    confidence_score=insight_data.get('confidence', 0.5),
                    priority_level=insight_data.get('priority', 'medium')
                )
                db.session.add(insight)
                saved_insights.append(insight)
            
            db.session.commit()
            return saved_insights

    except Exception as e:
        logger.error(f"Error generating predictive insights: {e}")
        return []
