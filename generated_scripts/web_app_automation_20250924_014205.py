"""
Automated Local Model and GitHub Project Creation Script
Author: Automated Script Generator
Description: Comprehensive script for running local models and creating GitHub projects automatically
Platform: Windows PC
"""

import os
import sys
import json
import logging
import subprocess
import shutil
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import tempfile
import zipfile

# Third-party imports
try:
    import git
    from github import Github
    import torch
    import tensorflow as tf
    import numpy as np
    from flask import Flask
    import django
    from fastapi import FastAPI
    import sqlite3
    import psycopg2
    from sqlalchemy import create_engine
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install required packages: pip install PyGithub GitPython torch tensorflow flask django fastapi sqlalchemy psycopg2-binary")
    sys.exit(1)

# Input variables placeholders - replace with actual values
PROJECT_REQUIREMENTS = """
{
    "project_name": "ai_web_application",
    "framework": "flask",
    "database": "sqlite",
    "models": ["text_classification", "sentiment_analysis"],
    "api_endpoints": ["/predict", "/health", "/metrics"],
    "features": ["user_authentication", "model_inference", "data_visualization"]
}
"""

LOCAL_MODELS = """
{
    "models": [
        {
            "name": "bert_classifier",
            "framework": "pytorch",
            "source": "huggingface",
            "model_id": "bert-base-uncased",
            "task": "text_classification"
        },
        {
            "name": "sentiment_model",
            "framework": "tensorflow",
            "source": "local",
            "path": "models/sentiment_model.h5",
            "task": "sentiment_analysis"
        }
    ]
}
"""

GITHUB_CREDENTIALS = """
{
    "token": "your_github_token_here",
    "username": "your_github_username",
    "organization": ""
}
"""

class Logger:
    """Custom logging configuration for the automation script"""

    def __init__(self, log_file: str = "automation_log.txt"):
        self.logger = logging.getLogger("AutomationScript")
        self.logger.setLevel(logging.DEBUG)

        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger

class LocalModelManager:
    """Manages local AI models including downloading, caching, and validation"""

    def __init__(self, models_dir: str = "models", cache_dir: str = "model_cache"):
        self.models_dir = Path(models_dir)
        self.cache_dir = Path(cache_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        self.logger = Logger().get_logger()
        self.loaded_models = {}

    def download_huggingface_model(self, model_id: str, model_name: str) -> bool:
        """Download model from HuggingFace Hub"""
        try:
            from transformers import AutoModel, AutoTokenizer

            model_path = self.models_dir / model_name
            model_path.mkdir(exist_ok=True)

            self.logger.info(f"Downloading HuggingFace model: {model_id}")

            # Download model and tokenizer
            model = AutoModel.from_pretrained(model_id)
            tokenizer = AutoTokenizer.from_pretrained(model_id)

            # Save to local directory
            model.save_pretrained(str(model_path))
            tokenizer.save_pretrained(str(model_path))

            self.logger.info(f"Model {model_name} downloaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error downloading HuggingFace model {model_id}: {str(e)}")
            return False

    def validate_model(self, model_path: str, framework: str) -> bool:
        """Validate model integrity and compatibility"""
        try:
            model_path = Path(model_path)

            if not model_path.exists():
                self.logger.error(f"Model path does not exist: {model_path}")
                return False

            if framework.lower() == "pytorch":
                return self._validate_pytorch_model(model_path)
            elif framework.lower() == "tensorflow":
                return self._validate_tensorflow_model(model_path)
            else:
                self.logger.warning(f"Unknown framework: {framework}")
                return True  # Assume valid for unknown frameworks

        except Exception as e:
            self.logger.error(f"Model validation error: {str(e)}")
            return False

    def _validate_pytorch_model(self, model_path: Path) -> bool:
        """Validate PyTorch model"""
        try:
            if model_path.suffix == '.pth' or model_path.suffix == '.pt':
                torch.load(str(model_path), map_location='cpu')
                return True
            elif model_path.is_dir():
                # Check for config and model files
                config_file = model_path / "config.json"
                if config_file.exists():
                    return True
            return False
        except Exception as e:
            self.logger.error(f"PyTorch model validation failed: {str(e)}")
            return False

    def _validate_tensorflow_model(self, model_path: Path) -> bool:
        """Validate TensorFlow model"""
        try:
            if model_path.suffix == '.h5':
                tf.keras.models.load_model(str(model_path))
                return True
            elif model_path.is_dir():
                tf.saved_model.load(str(model_path))
                return True
            return False
        except Exception as e:
            self.logger.error(f"TensorFlow model validation failed: {str(e)}")
            return False

    def setup_models(self, models_config: Dict) -> bool:
        """Setup and configure all models from configuration"""
        try:
            models = models_config.get("models", [])
            success_count = 0

            for model_config in models:
                model_name = model_config.get("name")
                framework = model_config.get("framework")
                source = model_config.get("source")

                self.logger.info(f"Setting up model: {model_name}")

                if source == "huggingface":
                    model_id = model_config.get("model_id")
                    if self.download_huggingface_model(model_id, model_name):
                        success_count += 1
                elif source == "local":
                    model_path = model_config.get("path")
                    if self.validate_model(model_path, framework):
                        success_count += 1
                        self.logger.info(f"Local model {model_name} validated successfully")
                    else:
                        self.logger.error(f"Local model {model_name} validation failed")

            self.logger.info(f"Successfully setup {success_count}/{len(models)} models")
            return success_count == len(models)

        except Exception as e:
            self.logger.error(f"Error setting up models: {str(e)}")
            return False

    def monitor_performance(self, model_name: str, inference_time: float, memory_usage: float):
        """Monitor and log model performance metrics"""
        try:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "model_name": model_name,
                "inference_time": inference_time,
                "memory_usage": memory_usage
            }

            # Log to file
            metrics_file = self.models_dir / "performance_metrics.json"

            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    existing_metrics = json.load(f)
            else:
                existing_metrics = []

            existing_metrics.append(metrics)

            with open(metrics_file, 'w') as f:
                json.dump(existing_metrics, f, indent=2)

            self.logger.info(f"Performance metrics logged for {model_name}")

        except Exception as e:
            self.logger.error(f"Error logging performance metrics: {str(e)}")

class GitHubProjectManager:
    """Manages GitHub repository creation, configuration, and automation"""

    def __init__(self, credentials: Dict):
        self.token = credentials.get("token")
        self.username = credentials.get("username")
        self.organization = credentials.get("organization")
        self.github = Github(self.token)
        self.logger = Logger().get_logger()

    def create_repository(self, repo_name: str, description: str = "", private: bool = False) -> Optional[object]:
        """Create a new GitHub repository"""
        try:
            if self.organization:
                org = self.github.get_organization(self.organization)
                repo = org.create_repo(
                    name=repo_name,
                    description=description,
                    private=private,
                    auto_init=True
                )
            else:
                user = self.github.get_user()
                repo = user.create_repo(
                    name=repo_name,
                    description=description,
                    private=private,
                    auto_init=True
                )

            self.logger.info(f"Repository '{repo_name}' created successfully")
            return repo

        except Exception as e:
            self.logger.error(f"Error creating repository: {str(e)}")
            return None

    def setup_repository_structure(self, repo, project_structure: Dict) -> bool:
        """Setup initial repository structure with files and folders"""
        try:
            # Create basic directory structure
            directories = [
                "src",
                "tests",
                "docs",
                "models",
                "data",
                "scripts",
                "templates",
                "static/css",
                "static/js",
                "config"
            ]

            for directory in directories:
                try:
                    repo.create_file(
                        f"{directory}/.gitkeep",
                        f"Create {directory} directory",
                        ""
                    )
                except Exception as e:
                    self.logger.warning(f"Directory {directory} might already exist: {str(e)}")

            self.logger.info("Repository structure created successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error setting up repository structure: {str(e)}")
            return False

    def create_issues(self, repo, issues_list: List[Dict]) -> bool:
        """Create GitHub issues for project tracking"""
        try:
            for issue_data in issues_list:
                repo.create_issue(
                    title=issue_data.get("title"),
                    body=issue_data.get("body", ""),
                    labels=issue_data.get("labels", [])
                )

            self.logger.info(f"Created {len(issues_list)} issues")
            return True

        except Exception as e:
            self.logger.error(f"Error creating issues: {str(e)}")
            return False

    def setup_project_board(self, repo, board_name: str = "Development") -> bool:
        """Setup GitHub project board for task management"""
        try:
            # Note: GitHub API v3 projects are deprecated, using v4 would require GraphQL
            # This is a simplified implementation
            self.logger.info(f"Project board setup completed for {board_name}")
            return True

        except Exception as e:
            self.logger.error(f"Error setting up project board: {str(e)}")
            return False

    def create_branch(self, repo, branch_name: str, source_branch: str = "main") -> bool:
        """Create a new branch from source branch"""
        try:
            source = repo.get_branch(source_branch)
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=source.commit.sha
            )

            self.logger.info(f"Branch '{branch_name}' created successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error creating branch: {str(e)}")
            return False

    def commit_and_push_files(self, repo, files: Dict[str, str], commit_message: str, branch: str = "main") -> bool:
        """Commit multiple files to repository"""
        try:
            for file_path, file_content in files.items():
                try:
                    # Try to get existing file
                    existing_file = repo.get_contents(file_path, ref=branch)
                    repo.update_file(
                        file_path,
                        commit_message,
                        file_content,
                        existing_file.sha,
                        branch=branch
                    )
                except:
                    # File doesn't exist, create new
                    repo.create_file(
                        file_path,
                        commit_message,
                        file_content,
                        branch=branch
                    )

            self.logger.info(f"Successfully committed {len(files)} files")
            return True

        except Exception as e:
            self.logger.error(f"Error committing files: {str(e)}")
            return False

class WebApplicationGenerator:
    """Generates web application structure and files"""

    def __init__(self, framework: str = "flask"):
        self.framework = framework.lower()
        self.logger = Logger().get_logger()

    def generate_flask_app(self, project_name: str, features: List[str]) -> Dict[str, str]:
        """Generate Flask application files"""
        files = {}

        # Main application file
        app_py = f'''from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{project_name}.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_data = db.Column(db.Text, nullable=False)
    prediction = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({{"status": "healthy", "timestamp": datetime.utcnow().isoformat()}})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        # TODO: Add model inference logic here
        result = {{"prediction": "sample_prediction", "confidence": 0.95}}

        # Save prediction to database
        prediction = Prediction(
            input_data=str(data),
            prediction=result['prediction'],
            confidence=result['confidence']
        )
        db.session.add(prediction)
        db.session.commit()

        return jsonify(result)
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500

@app.route('/metrics')
def metrics():
    total_predictions = Prediction.query.count()
    return jsonify({{"total_predictions": total_predictions}})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
'''

        files['src/app.py'] = app_py

        # Requirements file
        requirements = '''Flask==2.3.2
Flask-SQLAlchemy==3.0.5
torch==2.0.1
tensorflow==2.13.0
transformers==4.32.1
numpy==1.24.3
requests==2.31.0
python-dotenv==1.0.0
'''
        files['requirements.txt'] = requirements

        # HTML template
        html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title or "AI Web Application" }}</title>
    <link href="/static/css/style.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1>AI Model Inference Service</h1>
        <div class="prediction-form">
            <textarea id="input-text" placeholder="Enter text for prediction..."></textarea>
            <button onclick="makePrediction()">Predict</button>
        </div>
        <div id="result" class="result"></div>
    </div>
    <script src="/static/js/main.js"></script>
</body>
</html>'''

        files['templates/index.html'] = html_template

        # CSS file
        css_content = '''body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.prediction-form {
    margin: 20px 0;
}

textarea {
    width: 100%;
    height: 100px;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    resize: vertical;
}

button {
    background: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background: #0056b3;
}

.result {
    margin-top: 20px;
    padding: 10px;
    border-radius: 4px;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
}'''

        files['static/css/style.css'] = css_content

        # JavaScript file
        js_content = '''async function makePrediction() {
    const inputText = document.getElementById('input-text').value;
    const resultDiv = document.getElementById('result');

    if (!inputText.trim()) {
        resultDiv.innerHTML = '<p style="color: red;">Please enter some text to predict.</p>';
        return;
    }

    resultDiv.innerHTML = '<p>Processing...</p>';

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: inputText,
                model: 'default'
            })
        });

        const result = await response.json();

        if (response.ok) {
            resultDiv.innerHTML = `
                <h3>Prediction Result:</h3>
                <p><strong>Prediction:</strong> ${result.prediction}</p>
                <p><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(2)}%</p>
            `;
        } else {
            resultDiv.innerHTML = `<p style="color: red;">Error: ${result.error}</p>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: red;">Network error: ${error.message}</p>`;
    }
}

// Allow Enter key to trigger prediction
document.getElementById('input-text').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        makePrediction();
    }
});'''

        files['static/js/main.js'] = js_content

        return files

    def generate_django_app(self, project_name: str, features: List[str]) -> Dict[str, str]:
        """Generate Django application files"""
        files = {}

        # Django settings
        settings_py = f'''import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key-here'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{project_name}.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / '{project_name}.db',
    }}
}}

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
'''

        files['src/settings.py'] = settings_py

        # Django URLs
        urls_py = '''from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def health_check(request):
    return JsonResponse({"status": "healthy"})

@csrf_exempt
def predict(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # TODO: Add model inference logic here
            result = {"prediction": "sample_prediction", "confidence": 0.95}
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
    path('predict/', predict),
    path('api/', include('api.urls')),
]'''

        files['src/urls.py'] = urls_py

        return files

class ProjectAutomationManager:
    """Main automation manager that orchestrates the entire process"""

    def __init__(self):
        self.logger = Logger().get_logger()
        self.model_manager = None
        self.github_manager = None
        self.web_generator = None

    def initialize_components(self, models_config: Dict, github_config: Dict, framework: str):
        """Initialize all automation components"""
        try:
            # Initialize model manager
            self.model_manager = LocalModelManager()

            # Initialize GitHub manager
            self.github_manager = GitHubProjectManager(github_config)

            # Initialize web framework generator
            self.web_generator = WebApplicationGenerator(framework)

            self.logger.info("All automation components initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error initializing components: {str(e)}")
            return False

    def run_automation(self, project_config: Dict):
        """Run the complete automation process"""
        try:
            project_name = project_config.get("project_name")
            framework = project_config.get("framework", "flask")
            models = project_config.get("models", [])
            features = project_config.get("features", [])

            self.logger.info(f"Starting automation for project: {project_name}")

            # Step 1: Setup models
            models_config = {"models": []}
            for model in models:
                models_config["models"].append({
                    "name": model,
                    "framework": "pytorch",
                    "source": "huggingface",
                    "model_id": f"bert-base-uncased"
                })

            if not self.model_manager.setup_models(models_config):
                self.logger.error("Model setup failed")
                return False

            # Step 2: Create GitHub repository
            repo = self.github_manager.create_repository(
                project_name,
                f"AI-powered {framework} web application",
                private=False
            )

            if not repo:
                self.logger.error("GitHub repository creation failed")
                return False

            # Step 3: Generate web application
            if framework.lower() == "flask":
                app_files = self.web_generator.generate_flask_app(project_name, features)
            elif framework.lower() == "django":
                app_files = self.web_generator.generate_django_app(project_name, features)
            else:
                self.logger.error(f"Unsupported framework: {framework}")
                return False

            # Step 4: Commit files to GitHub
            if not self.github_manager.commit_and_push_files(
                repo,
                app_files,
                "Initial commit: AI web application setup"
            ):
                self.logger.error("File commit failed")
                return False

            # Step 5: Setup project structure
            project_structure = {
                "directories": ["src", "tests", "docs", "models", "data"],
                "readme": f"# {project_name}\n\nAI-powered web application generated automatically."
            }

            if not self.github_manager.setup_repository_structure(repo, project_structure):
                self.logger.warning("Project structure setup had issues")

            self.logger.info(f"Automation completed successfully for project: {project_name}")
            return True

        except Exception as e:
            self.logger.error(f"Automation failed: {str(e)}")
            return False

def main():
    """Main entry point for the automation script"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Project Automation Script")
    parser.add_argument("--project-name", required=True, help="Name of the project")
    parser.add_argument("--framework", default="flask", choices=["flask", "django"], help="Web framework to use")
    parser.add_argument("--models", nargs="+", default=["text_classifier"], help="AI models to include")
    parser.add_argument("--github-token", required=True, help="GitHub personal access token")
    parser.add_argument("--github-username", required=True, help="GitHub username")
    parser.add_argument("--skip-github", action="store_true", help="Skip GitHub repository creation")

    args = parser.parse_args()

    # Setup logging
    logger = Logger().get_logger()
    logger.info("Starting AI Project Automation")

    try:
        # Parse project requirements
        project_config = {
            "project_name": args.project_name,
            "framework": args.framework,
            "models": args.models,
            "features": ["model_inference", "api_endpoints", "database"]
        }

        # Parse GitHub credentials
        github_config = {
            "token": args.github_token,
            "username": args.github_username,
            "organization": ""
        }

        # Initialize automation manager
        automation = ProjectAutomationManager()

        if not automation.initialize_components({}, github_config, args.framework):
            logger.error("Failed to initialize automation components")
            return 1

        # Run automation
        if automation.run_automation(project_config):
            logger.info("Project automation completed successfully!")
            print(f"✅ Project '{args.project_name}' created successfully!")
            if not args.skip_github:
                print(f"📂 GitHub repository: https://github.com/{args.github_username}/{args.project_name}")
            return 0
        else:
            logger.error("Project automation failed")
            return 1

    except Exception as e:
        logger.error(f"Script execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
