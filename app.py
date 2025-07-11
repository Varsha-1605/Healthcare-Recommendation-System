# import os
# import logging
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_socketio import SocketIO
# from sqlalchemy.orm import DeclarativeBase
# from werkzeug.middleware.proxy_fix import ProxyFix

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# class Base(DeclarativeBase):
#     pass

# # Initialize Flask app
# app = Flask(__name__)
# app.secret_key = os.environ.get("SESSION_SECRET", "healthcare-secret-key-2024")
# app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# # Database configuration
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///healthcare_ai.db")
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
#     "pool_recycle": 300,
#     "pool_pre_ping": True,
# }

# # Initialize extensions
# db = SQLAlchemy(app, model_class=Base)
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# # API Configuration
# HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', 'hf_default_key')
# GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'gemini_default_key')

# # Hugging Face API endpoints
# HF_API_BASE = "https://api-inference.huggingface.co/models"
# HF_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# # Medical NLP models
# BIOMEDICAL_NER_MODEL = "d4data/biomedical-ner-all"
# MEDICAL_QA_MODEL = "deepset/roberta-base-squad2"
# CLINICAL_CLASSIFIER_MODEL = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"

# # Custom Jinja2 filter to convert newlines to <br> tags
# @app.template_filter('nl2br')
# def nl2br_filter(s):
#     if s is None:
#         return ""
#     return s.replace('\n', '<br>')

# # Create tables
# with app.app_context():
#     import models  # noqa: F401
#     db.create_all()
#     logger.info("Database tables created")











import eventlet
eventlet.monkey_patch()


import os
import json
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "healthcare-secret-key-2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///healthcare_ai.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db = SQLAlchemy(app, model_class=Base)
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
# API Configuration
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', 'hf_default_key')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'gemini_default_key')

# Hugging Face API endpoints
HF_API_BASE = "https://api-inference.huggingface.co/models"
HF_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# Medical NLP models
BIOMEDICAL_NER_MODEL = "d4data/biomedical-ner-all"
MEDICAL_QA_MODEL = "deepset/roberta-base-squad2"
CLINICAL_CLASSIFIER_MODEL = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"

# Custom Jinja2 filters
@app.template_filter('nl2br')
def nl2br_filter(s):
    if s is None:
        return ""
    return s.replace('\n', '<br>')

@app.template_filter('from_json')
def from_json_filter(s):
    if s is None:
        return []
    try:
        return json.loads(s)
    except:
        return []

# Create tables
with app.app_context():
    import models  # noqa: F401
    db.create_all()
    logger.info("Database tables created")


    # >>> ADD THESE TWO LINES HERE <<<
    import populate_data # Import the populate_data script
    populate_data.populate_sample_content()
    logger.info("Database population script executed (if not already populated)!")
    # >>> END ADDITIONS <<<

import routes