#!/usr/bin/env python3
"""
Script to populate the HealthAI database with sample content
Run this script to add sample health content for testing and demonstration
"""

import json
from datetime import datetime
from app import app, db
from models import HealthContent, User, PredictiveInsight

def populate_sample_content():
    """Add sample health content to the database"""
    
    sample_content = [
        # Cardiology content
        {
            'title': 'Understanding Heart Health: A Complete Guide',
            'content_type': 'article',
            'category': 'cardiology',
            'description': 'Learn about maintaining a healthy heart through diet, exercise, and lifestyle changes. This comprehensive guide covers everything from understanding cholesterol levels to recognizing early warning signs of heart disease.',
            'content_url': '#',
            'image_url': 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800',
            'tags': '["heart health", "cardiology", "prevention", "lifestyle"]',
            'difficulty_level': 'beginner',
            'duration': 15,
            'target_age_min': 18,
            'target_age_max': 80,
            'target_conditions': '["hypertension", "high cholesterol"]',
            'popularity_score': 8.5
        },
        {
            'title': 'Cardio Workout for Heart Strength',
            'content_type': 'exercise',
            'category': 'cardiology',
            'description': 'A 30-minute cardiovascular workout designed to strengthen your heart and improve circulation. Suitable for beginners and intermediate fitness levels.',
            'content_url': '#',
            'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800',
            'tags': '["cardio", "exercise", "heart health", "fitness"]',
            'difficulty_level': 'intermediate',
            'duration': 30,
            'target_age_min': 16,
            'target_age_max': 65,
            'target_conditions': '["heart disease", "obesity"]',
            'popularity_score': 7.8
        },
        
        # Nutrition content
        {
            'title': 'Mediterranean Diet: Heart-Healthy Eating Plan',
            'content_type': 'diet',
            'category': 'nutrition',
            'description': 'Discover the benefits of the Mediterranean diet for heart health, weight management, and overall wellness. Includes meal plans and recipe suggestions.',
            'content_url': '#',
            'image_url': 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800',
            'tags': '["mediterranean diet", "nutrition", "heart health", "recipes"]',
            'difficulty_level': 'beginner',
            'duration': 20,
            'target_age_min': 18,
            'target_age_max': 75,
            'target_conditions': '["heart disease", "diabetes", "obesity"]',
            'popularity_score': 9.2
        },
        {
            'title': 'Healthy Meal Prep for Busy Professionals',
            'content_type': 'article',
            'category': 'nutrition',
            'description': 'Learn how to prepare nutritious meals in advance to maintain a healthy diet despite a busy schedule. Tips, tricks, and easy recipes included.',
            'content_url': '#',
            'image_url': 'https://images.unsplash.com/photo-1547496502-affa22d38842?w=800',
            'tags': '["meal prep", "nutrition", "busy lifestyle", "healthy eating"]',
            'difficulty_level': 'beginner',
            'duration': 12,
            'target_age_min': 22,
            'target_age_max': 55,
            'target_conditions': '["obesity", "diabetes"]',
            'popularity_score': 8.1
        },
        
        # Fitness content
        {
            'title': 'Beginner Yoga for Stress Relief',
            'content_type': 'exercise',
            'category': 'mental_health',
            'description': 'A gentle yoga routine designed to reduce stress and improve mental clarity. Perfect for beginners who want to start their wellness journey.',
            'content_url': '#',
            'image_url': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800',
            'tags': '["yoga", "stress relief", "mental health", "beginner"]',
            'difficulty_level': 'beginner',
            'duration': 25,
            'target_age_min': 16,
            'target_age_max': 70,
            'target_conditions': '["anxiety", "stress", "depression"]',
            'popularity_score': 8.7
        },
        {
            'title': 'High-Intensity Interval Training (HIIT) Basics',
            'content_type': 'exercise',
            'category': 'fitness',
            'description': 'Learn the fundamentals of HIIT training for maximum fat burn and fitness gains. Includes beginner-friendly routines and safety tips.',
            'content_url': '#',
            'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800',
            'tags': '["HIIT", "fitness", "weight loss", "strength training"]',
            'difficulty_level': 'intermediate',
            'duration': 35,
            'target_age_min': 18,
            'target_age_max': 45,
            'target_conditions': '["obesity", "low fitness"]',
            'popularity_score': 7.9
        },
        
        # Mental Health content
        {
            'title': 'Managing Anxiety: Practical Strategies',
            'content_type': 'article',
            'category': 'mental_health',
            'description': 'Evidence-based techniques for managing anxiety and improving mental well-being. Includes breathing exercises and cognitive strategies.',
            'content_url': '#',
            'image_url': 'https://images.unsplash.com/photo-1499209974431-9dddcece7f88?w=800',
            'tags': '["anxiety", "mental health", "coping strategies", "wellness"]',
            'difficulty_level': 'beginner',
            'duration': 18,
            'target_age_min': 16,
            'target_age_max': 65,
            'target_conditions': '["anxiety", "stress", "panic disorder"]',
            'popularity_score': 8.9
        },
        {
            'title': 'Meditation for Better Sleep',
            'content_type': 'video',
            'category': 'mental_health',
            'description': 'Guided meditation techniques to improve sleep quality and overcome insomnia. Learn relaxation methods for better rest.',
            'content_url': '#',
            'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
            'tags': '["meditation", "sleep", "relaxation", "insomnia"]',
            'difficulty_level': 'beginner',
            'duration': 22,
            'target_age_min': 18,
            'target_age_max': 70,
            'target_conditions': '["insomnia", "stress", "anxiety"]',
            'popularity_score': 8.3
        },
        
        # Diabetes & Preventive Care
        {
            'title': 'Diabetes Prevention: Lifestyle Changes That Matter',
            'content_type': 'article',
            'category': 'preventive_care',
            'description': 'Learn how to prevent type 2 diabetes through diet, exercise, and lifestyle modifications. Early intervention strategies explained.',
            'content_url': '#',
            'image_url': 'https://images.unsplash.com/photo-1559757175-0eb30cd8c063?w=800',
            'tags': '["diabetes prevention", "lifestyle", "diet", "exercise"]',
            'difficulty_level': 'beginner',
            'duration': 16,
            'target_age_min': 25,
            'target_age_max': 65,
            'target_conditions': '["prediabetes", "obesity", "family history"]',
            'popularity_score': 8.6
        },
        {
            'title': 'Understanding Blood Sugar Monitoring',
            'content_type': 'treatment',
            'category': 'diabetes_care',
            'description': 'Complete guide to blood sugar monitoring for diabetes management. Learn when to test, how to interpret results, and when to seek help.',
            'content_url': '#',
            'image_url': 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800',
            'tags': '["blood sugar", "diabetes", "monitoring", "self-care"]',
            'difficulty_level': 'intermediate',
            'duration': 14,
            'target_age_min': 18,
            'target_age_max': 80,
            'target_conditions': '["diabetes", "prediabetes"]',
            'popularity_score': 7.7
        }
    ]
    
    print("Adding sample health content...")
    
    for content_data in sample_content:
        # Check if content already exists
        existing = HealthContent.query.filter_by(title=content_data['title']).first()
        if not existing:
            content = HealthContent(**content_data)
            db.session.add(content)
    
    try:
        db.session.commit()
        print(f"✅ Successfully added {len(sample_content)} health content items!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error adding content: {e}")

def add_sample_insights(user_id):
    """Add sample predictive insights for a user"""
    
    sample_insights = [
        {
            'user_id': user_id,
            'insight_type': 'health_risk',
            'title': 'Cardiovascular Health Assessment',
            'description': 'Based on your activity patterns and health profile, maintaining regular cardio exercise could reduce your risk of heart disease by 30%.',
            'confidence_score': 0.82,
            'priority_level': 'medium',
            'is_active': True
        },
        {
            'user_id': user_id,
            'insight_type': 'wellness_trend',
            'title': 'Improved Sleep Pattern Detected',
            'description': 'Your recent health activities suggest improved sleep hygiene. Continue current practices for optimal rest and recovery.',
            'confidence_score': 0.75,
            'priority_level': 'low',
            'is_active': True
        },
        {
            'user_id': user_id,
            'insight_type': 'recommendation',
            'title': 'Nutrition Optimization Opportunity',
            'description': 'Consider incorporating more Mediterranean diet principles. This could improve your overall health metrics by 25%.',
            'confidence_score': 0.88,
            'priority_level': 'high',
            'is_active': True
        }
    ]
    
    for insight_data in sample_insights:
        insight = PredictiveInsight(**insight_data)
        db.session.add(insight)
    
    try:
        db.session.commit()
        print(f"✅ Added {len(sample_insights)} sample insights for user {user_id}")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error adding insights: {e}")

if __name__ == '__main__':
    with app.app_context():
        print("🏥 Populating HealthAI database with sample data...")
        populate_sample_content()
        print("✅ Database population complete!")
        print("\nTo run from command line:")
        print("python populate_data.py")