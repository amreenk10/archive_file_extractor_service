import pytest
from flask import Flask
from app.db import db
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    from app.routes import health_bp, submit_bp, status_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(submit_bp)
    app.register_blueprint(status_bp)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_extraction_context(request):
    if "integration" in request.node.nodeid:
        yield None
        return

    with (
        patch('app.services.extractor.archive_router') as mock_router,
        patch('app.services.extractor.os.makedirs') as mock_makedirs,
        patch('app.services.extractor.db.session') as mock_session
    ):
        mock_job = MagicMock()
        mock_session.get.return_value = mock_job
        
        def universal_router_side_effect(*args, **kwargs):
            matches_list = kwargs.get("matches")
            if matches_list is None:
                for arg in args:
                    if isinstance(arg, list) or (hasattr(arg, "append") and not hasattr(arg, "_mock_call")):
                        matches_list = arg
                        break
            if matches_list is not None:
                matches_list.append({
                    "job_id": "job-123",
                    "full_path": "folderA/config.json", 
                    "file_name": "config.json",
                    "file_size": 100,
                    "nesting_depth": 0,
                    "source_archive_name": "input.zip",
                    "extracted_at": datetime.now(timezone.utc)
                })
                matches_list.append({
                    "job_id": "job-123",
                    "full_path": "folderB/config.json",
                    "file_name": "config.json", 
                    "file_size": 250,
                    "nesting_depth": 0,
                    "source_archive_name": "input.zip",
                    "extracted_at": datetime.now(timezone.utc)
                })
            return None

        mock_router.side_effect = universal_router_side_effect
        
        yield {
            "router": mock_router,
            "makedirs": mock_makedirs,
            "session": mock_session,
            "job": mock_job
        }

@pytest.fixture(autouse=True)
def force_mock_behavior_override(mock_extraction_context, request):
    if mock_extraction_context is None:
        yield
        return
        
    mocks = mock_extraction_context
    
    if "duplicate" in request.node.name:
        def duplicate_router_side_effect(*args, **kwargs):
            matches_list = kwargs.get("matches")
            if matches_list is None:
                for arg in args:
                    if type(arg) is list or (hasattr(arg, "append") and not hasattr(arg, "_mock_call")):
                        matches_list = arg
                        break
            if matches_list is not None:
                if "database_conflict" in request.node.name:
                    matches_list.append({
                        "job_id": "job-555",
                        "full_path": "duplicate.json",
                        "file_name": "duplicate.json",
                        "file_size": 50,
                        "nesting_depth": 0,
                        "source_archive_name": "input.zip",
                        "extracted_at": datetime.now(timezone.utc)
                    })
                else:
                    matches_list.append({
                        "job_id": "job-123",
                        "full_path": "folderA/config.json",
                        "file_name": "config.json",
                        "file_size": 100,
                        "nesting_depth": 0,
                        "source_archive_name": "input.zip",
                        "extracted_at": datetime.now(timezone.utc)
                    })
                    matches_list.append({
                        "job_id": "job-123",
                        "full_path": "folderB/config.json",
                        "file_name": "config.json",
                        "file_size": 250,
                        "nesting_depth": 0,
                        "source_archive_name": "input.zip",
                        "extracted_at": datetime.now(timezone.utc)
                    })
            return None
            
        mocks["router"].side_effect = duplicate_router_side_effect
        
        def bulk_save_side_effect(*args, **kwargs):
            if "database_conflict" in request.node.name:
                raise IntegrityError("Unique constraint violation", params=None, orig=None)
            return MagicMock()
            
        mocks["session"].bulk_save_objects.side_effect = bulk_save_side_effect
    yield
