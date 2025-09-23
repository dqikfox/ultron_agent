"""
Automated Local Model and GitHub Project Management Script
Comprehensive solution for Windows PC automation of ML model deployment and GitHub project creation
"""

import os
import sys
import json
import logging
import subprocess
import shutil
import tempfile
import time
import hashlib
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse
import configparser

# Third-party imports
try:
    import requests
    import git
    from github import Github
    import torch
    import tensorflow as tf
    from transformers import AutoModel, AutoTokenizer
    import psutil
    import yaml
    from jinja2 import Environment, FileSystemLoader
    from flask import Flask
    import django
    from fastapi import FastAPI
    import sqlite3
    import psycopg2
    from sqlalchemy import create_engine
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install required packages using: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProjectRequirements:
    """Parse and manage project requirements configuration"""
    
    def __init__(self, requirements_data: str):
        """
        Initialize project requirements from JSON string or dict
        
        Args:
            requirements_data: JSON string or dictionary containing project specifications
        """
        try:
            if isinstance(requirements_data, str):
                self.data = json.loads(requirements_data)
            else:
                self.data = requirements_data
            self.validate_requirements()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in project requirements: {e}")
            raise
        except Exception as e:
            logger.error(f"Error initializing project requirements: {e}")
            raise
    
    def validate_requirements(self):
        """Validate required fields in project requirements"""
        required_fields = ['project_name', 'framework', 'models', 'database']
        for field in required_fields:
            if field not in self.data:
                raise ValueError(f"Missing required field: {field}")
    
    @property
    def project_name(self) -> str:
        return self.data['project_name']
    
    @property
    def framework(self) -> str:
        return self.data.get('framework', 'flask')
    
    @property
    def models(self) -> List[str]:
        return self.data.get('models', [])
    
    @property
    def database(self) -> str:
        return self.data.get('database', 'sqlite')
    
    @property
    def features(self) -> List[str]:
        return self.data.get('features', [])

class LocalModelManager:
    """Manage local ML models including download, caching, and validation"""
    
    def __init__(self, models_config: str, cache_dir: str = None):
        """
        Initialize local model manager
        
        Args:
            models_config: JSON string or dict with model configurations
            cache_dir: Directory for model caching (default: ./models_cache)
        """
        try:
            if isinstance(models_config, str):
                self.models_config = json.loads(models_config)
            else:
                self.models_config = models_config
            
            self.cache_dir = Path(cache_dir) if cache_dir else Path("models_cache")
            self.cache_dir.mkdir(exist_ok=True)
            
            # Model registry for loaded models
            self.loaded_models = {}
            self.model_metadata = {}
            
        except Exception as e:
            logger.error(f"Error initializing model manager: {e}")
            raise
    
    def download_model(self, model_name: str, model_url: str = None) -> bool:
        """
        Download and cache model from various sources
        
        Args:
            model_name: Name/identifier of the model
            model_url: Optional URL for direct download
            
        Returns:
            bool: Success status
        """
        try:
            model_path = self.cache_dir / model_name
            
            # Check if model already exists
            if model_path.exists():
                logger.info(f"Model {model_name} already cached")
                return True
            
            logger.info(f"Downloading model: {model_name}")
            
            # Handle different model sources
            if model_url:
                # Direct download from URL
                response = requests.get(model_url, stream=True)
                response.raise_for_status()
                
                with open(model_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            elif model_name in ['bert-base-uncased', 'gpt2', 'distilbert-base-uncased']:
                # Hugging Face models
                try:
                    model = AutoModel.from_pretrained(model_name, cache_dir=str(model_path))
                    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=str(model_path))
                    
                    # Store model metadata
                    self.model_metadata[model_name] = {
                        'type': 'huggingface',
                        'path': str(model_path),
                        'downloaded_at': datetime.now().isoformat()
                    }
                    
                except Exception as e:
                    logger.error(f"Error downloading HuggingFace model {model_name}: {e}")
                    return False
            
            else:
                # Try to download from model hub or custom source
                logger.warning(f"Unknown model source for {model_name}, skipping download")
                return False
            
            logger.info(f"Successfully downloaded model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading model {model_name}: {e}")
            return False
    
    def load_model(self, model_name: str, framework: str = 'pytorch') -> Any:
        """
        Load model into memory for inference
        
        Args:
            model_name: Name of the model to load
            framework: ML framework to use (pytorch, tensorflow)
            
        Returns:
            Loaded model object
        """
        try:
            if model_name in self.loaded_models:
                logger.info(f"Model {model_name} already loaded")
                return self.loaded_models[model_name]
            
            model_path = self.cache_dir / model_name
            
            if not model_path.exists():
                logger.info(f"Model {model_name} not cached, attempting download")
                if not self.download_model(model_name):
                    raise FileNotFoundError(f"Could not download model: {model_name}")
            
            logger.info(f"Loading model {model_name} with {framework}")
            
            if framework.lower() == 'pytorch':
                if model_name in ['bert-base-uncased', 'gpt2', 'distilbert-base-uncased']:
                    model = AutoModel.from_pretrained(str(model_path))
                    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
                    self.loaded_models[model_name] = {'model': model, 'tokenizer': tokenizer}
                else:
                    model = torch.load(str(model_path))
                    self.loaded_models[model_name] = model
            
            elif framework.lower() == 'tensorflow':
                model = tf.keras.models.load_model(str(model_path))
                self.loaded_models[model_name] = model
            
            else:
                raise ValueError(f"Unsupported framework: {framework}")
            
            logger.info(f"Successfully loaded model: {model_name}")
            return self.loaded_models[model_name]
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            raise
    
    def validate_model(self, model_name: str) -> bool:
        """
        Validate model integrity and functionality
        
        Args:
            model_name: Name of model to validate
            
        Returns:
            bool: Validation success status
        """
        try:
            model_path = self.cache_dir / model_name
            
            if not model_path.exists():
                logger.error(f"Model {model_name} not found for validation")
                return False
            
            # Basic file integrity check
            if model_path.is_file():
                if model_path.stat().st_size == 0:
                    logger.error(f"Model file {model_name} is empty")
                    return False
            
            # Try loading the model
            try:
                loaded_model = self.load_model(model_name)
                if loaded_model is None:
                    return False
            except Exception as e:
                logger.error(f"Model {model_name} failed to load during validation: {e}")
                return False
            
            logger.info(f"Model {model_name} validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Error validating model {model_name}: {e}")
            return False
    
    def get_model_performance_metrics(self, model_name: str) -> Dict:
        """
        Get performance metrics for a loaded model
        
        Args:
            model_name: Name of model to analyze
            
        Returns:
            Dictionary containing performance metrics
        """
        try:
            if model_name not in self.loaded_models:
                logger.warning(f"Model {model_name} not loaded, cannot get metrics")
                return {}
            
            # Basic system metrics
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            cpu_percent = psutil.cpu_percent()
            
            metrics = {
                'model_name': model_name,
                'memory_usage_mb': memory_usage,
                'cpu_percent': cpu_percent,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add model-specific metrics if available
            if hasattr(self.loaded_models[model_name], 'parameters'):
                try:
                    param_count = sum(p.numel() for p in self.loaded_models[model_name].parameters())
                    metrics['parameter_count'] = param_count
                except:
                    pass
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting performance metrics for {model_name}: {e}")
            return {}

class GitHubManager:
    """Manage GitHub repository operations and integrations"""
    
    def __init__(self, credentials: str):
        """
        Initialize GitHub manager with credentials
        
        Args:
            credentials: JSON string or dict with GitHub credentials
        """
        try:
            if isinstance(credentials, str):
                self.credentials = json.loads(credentials)
            else:
                self.credentials = credentials
            
            # Initialize GitHub API client
            token = self.credentials.get('token')
            if not token:
                raise ValueError("GitHub token is required")
            
            self.github = Github(token)
            self.user = self.github.get_user()
            
            logger.info(f"GitHub manager initialized for user: {self.user.login}")
            
        except Exception as e:
            logger.error(f"Error initializing GitHub manager: {e}")
            raise
    
    def create_repository(self, repo_name: str, description: str = "", private: bool = False) -> bool:
        """
        Create a new GitHub repository
        
        Args:
            repo_name: Name of the repository
            description: Repository description
            private: Whether repository should be private
            
        Returns:
            bool: Success status
        """
        try:
            # Check if repository already exists
            try:
                existing_repo = self.user.get_repo(repo_name)
                logger.info(f"Repository {repo_name} already exists")
                self.current_repo = existing_repo
                return True
            except:
                pass  # Repository doesn't exist, continue with creation
            
            logger.info(f"Creating GitHub repository: {repo_name}")
            
            repo = self.user.create_repo(
                name=repo_name,
                description=description,
                private=private,
                auto_init=True,
                gitignore_template="Python"
            )
            
            self.current_repo = repo
            logger.info(f"Successfully created repository: {repo_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating repository {repo_name}: {e}")
            return False
    
    def clone_repository(self, repo_name: str, local_path: str) -> bool:
        """
        Clone repository to local directory
        
        Args:
            repo_name: Name of repository to clone
            local_path: Local directory path for cloning
            
        Returns:
            bool: Success status
        """
        try:
            repo_url = f"https://github.com/{self.user.login}/{repo_name}.git"
            
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
            
            logger.info(f"Cloning repository {repo_name} to {local_path}")
            
            git.Repo.clone_from(repo_url, local_path)
            self.local_repo_path = local_path
            self.local_git_repo = git.Repo(local_path)
            
            logger.info(f"Successfully cloned repository to {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error cloning repository {repo_name}: {e}")
            return False
    
    def commit_and_push(self, commit_message: str, branch: str = "main") -> bool:
        """
        Commit changes and push to GitHub
        
        Args:
            commit_message: Git commit message
            branch: Branch name to push to
            
        Returns:
            bool: Success status
        """
        try:
            if not hasattr(self, 'local_git_repo'):
                logger.error("No local repository available for commit")
                return False
            
            logger.info(f"Committing and pushing changes: {commit_message}")
            
            # Add all changes
            self.local_git_repo.git.add(A=True)
            
            # Check if there are changes to commit
            if not self.local_git_repo.is_dirty() and len(self.local_git_repo.untracked_files) == 0:
                logger.info("No changes to commit")
                return True
            
            # Commit changes
            self.local_git_repo.index.commit(commit_message)
            
            # Push to remote
            origin = self.local_git_repo.remote(name='origin')
            origin.push(branch)
            
            logger.info("Successfully committed and pushed changes")
            return True
            
        except Exception as e:
            logger.error(f"Error committing and pushing: {e}")
            return False
    
    def create_branch(self, branch_name: str, source_branch: str = "main") -> bool:
        """
        Create a new branch in the repository
        
        Args:
            branch_name: Name of new branch
            source_branch: Source branch to branch from
            
        Returns:
            bool: Success status
        """
        try:
            if not hasattr(self, 'local_git_repo'):
                logger.error("No local repository available for branch creation")
                return False
            
            logger.info(f"Creating branch {branch_name} from {source_branch}")
            
            # Create new branch
            new_branch = self.local_git_repo.create_head(branch_name, source_branch)
            new_branch.checkout()
            
            logger.info(f"Successfully created and switched to branch {branch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating branch {branch_name}: {e}")
            return False
    
    def create_pull_request(self, title: str, body: str, head_branch: str, base_branch: str = "main") -> bool:
        """
        Create a pull request
        
        Args:
            title: PR title
            body: PR description
            head_branch: Source branch for PR
            base_branch: Target branch for PR
            
        Returns:
            bool: Success status
        """
        try:
            if not hasattr(self, 'current_repo'):
                logger.error("No current repository for pull request creation")
                return False
            
            logger.info(f"Creating pull request: {title}")
            
            pr = self.current_repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            
            logger.info(f"Successfully created pull request #{pr.number}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating pull request: {e}")
            return False
    
    def setup_project_board(self, board_name: str, columns: List[str] = None) -> bool:
        """
        Setup project board with columns
        
        Args:
            board_name: Name of the project board
            columns: List of column names
            
        Returns:
            bool: Success status
        """
        try:
            if not hasattr(self, 'current_repo'):
                logger.error("No current repository for project board setup")
                return False
            
            if columns is None:
                columns = ["To Do", "In Progress", "Done"]
            
            logger.info(f"Setting up project board: {board_name}")
            
            # Note: GitHub API v4 (GraphQL) is needed for project boards v2
            # This is a simplified implementation for classic project boards
            project = self.current_repo.create_project(board_name, "Automated project board")
            
            for column_name in columns:
                project.create_column(column_name)
            
            logger.info(f"Successfully created project board: {board_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating project board: {e}")
            return False

class WebFrameworkGenerator:
    """Generate web application frameworks and boilerplate code"""
    
    def __init__(self, project_path: str, framework: str):
        """
        Initialize web framework generator
        
        Args:
            project_path: Path to project directory
            framework: Web framework to use (flask, django, fastapi)
        """
        self.project_path = Path(project_path)
        self.framework = framework.lower()
        self.project_path.mkdir(exist_ok=True)
        
        # Setup Jinja2 for template generation
        template_dir = Path(__file__).parent / "templates"
        template_dir.mkdir(exist_ok=True)
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        logger.info(f"Initialized {framework} generator for {project_path}")
    
    def generate_flask_app(self, requirements: ProjectRequirements) -> bool:
        """
        Generate Flask application structure
        
        Args:
            requirements: Project requirements object
            
        Returns:
            bool: Success status
        """
        try:
            logger.info("Generating Flask application structure")
            
            # Create Flask app structure
            app_structure = {
                'app.py': self._get_flask_app_template(),
                'requirements.txt': self._get_flask_requirements(),
                'config.py': self._get_flask_config_template(),
                'models.py': self._get_flask_models_template(requirements),
                'routes.py': self._get_flask_routes_template(requirements),
                'templates/base.html': self._get_base_template(),
                'templates/index.html': self._get_index_template(),
                'static/css/style.css': self._get_css_template(),
                'static/js/main.js': self._get_js_template(),
                'migrations/': '',  # Directory placeholder
            }
            
            # Create files and directories
            for file_path, content in app_structure.items():
                full_path = self.project_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                if content:  # Only write content if provided
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
            
            # Generate model-specific routes and templates
            self._generate_flask_model_integration(requirements)
            
            logger.info("Successfully generated Flask application structure")
            return True
            
        except Exception as e:
            logger.error(f"Error generating Flask app: {e}")
            return False
    
    def generate_django_app(self, requirements: ProjectRequirements) -> bool:
        """
        Generate Django application structure
        
        Args:
            requirements: Project requirements object
            
        Returns:
            bool: Success status
        """
        try:
            logger.info("Generating Django application structure")
            
            project_name = requirements.project_name.replace('-', '_')
            
            # Create Django project using management commands
            os.chdir(self.project_path.parent)
            subprocess.run([
                sys.executable, '-m', 'django', 'startproject', 
                project_name, str(self.project_path)
            ], check=True)
            
            # Create Django app
            os.chdir(self.project_path)
            subprocess.run([
                sys.executable, 'manage.py', 'startapp', 'main'
            ], check=True)
            
            # Generate Django-specific files
            self._generate_django_settings(requirements)
            self._generate_django_models(requirements)
            self._generate_django_views(requirements)
            self._generate_django_urls(requirements)
            self._generate_django_templates(requirements)
            
            logger.info("Successfully generated Django application structure")
            return True
            
        except Exception as e:
            logger.error(f"Error generating Django app: {e}")
            return False
    
    def generate_fastapi_app(self, requirements: ProjectRequirements) -> bool:
        """
        Generate FastAPI application structure
        
        Args:
            requirements: Project requirements object
            
        Returns:
            bool: Success status
        """
        try:
            logger.info("Generating FastAPI application structure")
            
            # Create FastAPI app structure
            app_structure = {
                'main.py': self._get_fastapi_main_template(),
                'requirements.txt': self._get_fastapi_requirements(),
                'config.py': self._get_fastapi_config_template(),
                'models.py': self._get_fastapi_models_template(requirements),
                'routers/api.py': self._get_fastapi_router_template(requirements),
                'routers/__init__.py': '',
                'database.py': self._get_fastapi_database_template(requirements),
                'schemas.py': self._get_fastapi_schemas_template(requirements),
                'templates/index.html': self._get_fastapi_template(),
                'static/style.css': self._get_css_template(),
            }
            
            # Create files and directories
            for file_path, content in app_structure.items():
                full_path = self.project_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                if content:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
            
            # Generate model integration
            self._generate_fastapi_model_integration(requirements)
            
            logger.info("Successfully generated FastAPI application structure")
            return True
            
        except Exception as e:
            logger.error(f"Error generating FastAPI app: {e}")
            return False
    
    def setup_database(self, db_type: str, requirements: ProjectRequirements) -> bool:
        """
        Setup database configuration and migrations
        
        Args:
            db_type: Database type (sqlite, postgresql, mysql)
            requirements: Project requirements
            
        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Setting up {db_type} database configuration")
            
            if db_type.lower() == 'sqlite':
                db_config = {
                    'DATABASE_URL': f'sqlite:///{requirements.project_name}.db',
                    'DRIVER': 'sqlite3'
                }
            elif db_type.lower() == 'postgresql':
                db_config = {
                    'DATABASE_URL': 'postgresql://user:password@localhost/dbname',
                    'DRIVER': 'psycopg2'
                }
            elif db_type.lower() == 'mysql':
                db_config = {
                    'DATABASE_URL': 'mysql://user:password@localhost/dbname',
                    'DRIVER': 'pymysql'
                }
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            # Write database configuration
            db_config_path = self.project_path / 'db_config.json'
            with open(db_config_path, 'w') as f:
                json.dump(db_config, f, indent=2)
            
            # Create initial migration script
            if self.framework == 'flask':
                self._create_flask_migrations(requirements)
            elif self.framework == 'django':
                self._create_django_migrations(requirements)
            
            logger.info(f"Successfully configured {db_type} database")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up database: {e}")
            return False
    
    # Template methods for generating boilerplate code
    def _get_flask_app_template(self) -> str:
        return '''from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models and routes
from models import *
from routes import *

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
'''
    
    def _get_flask_requirements(self) -> str:
        return '''Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
python-dotenv==1.0.0
requests==2.31.0
torch==2.0.1
transformers==4.33.2
numpy==1.24.3
pandas==1.5.3
scikit-learn==1.3.0
'''
    
    def _get_flask_config_template(self) -> str:
        return '''import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
'''
    
    def _get_flask_models_template(self, requirements: ProjectRequirements) -> str:
        models_code = '''from app import db
from datetime import datetime

class ModelResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    output_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'model_name': self.model_name,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'created_at': self.created_at.isoformat()
        }

'''
        
        # Add model-specific classes based on requirements
        for model_name in requirements.models:
            model_class_name = ''.join(word.capitalize() for word in model_name.split('-'))
            models_code += f'''
class {model_class_name}Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_text = db.Column(db.Text, nullable=False)
    prediction = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
'''
        
        return models_code
    
    def _get_flask_routes_template(self, requirements: ProjectRequirements) -> str:
        return '''from flask import request, jsonify, render_template
from app import app, db
from models import ModelResult
import json

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        input_data = data.get('input_data')
        
        # TODO: Add actual model inference logic here
        # This is a placeholder response
        result = {
            'prediction': 'sample_prediction',
            'confidence': 0.95,
            'model_used': model_name
        }
        
        # Save result to database
        model_result = ModelResult(
            model_name=model_name,
            input_data=json.dumps(input_data),
            output_data=json.dumps(result)
        )
        db.session.add(model_result)
        db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/results')
def get_results():
    results = ModelResult.query.order_by(ModelResult.created_at.desc()).limit(10).all()
    return jsonify([result.to_dict() for result in results])
'''
    
    def _get_base_template(self) -> str:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ML Web App{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">ML Web App</a>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js">