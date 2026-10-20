import pytest
from app.db import db
from app.models import ExtractionLog, ExtractedFile

@pytest.fixture(autouse=True)
def mock_extraction_context():
    return None

@pytest.fixture(autouse=True)
def force_mock_behavior_override():
    return None


def test_get_status_success(client, app):
    with app.app_context():
        stub_job=ExtractionLog(
            id="123",
            status="RUNNING",
            pattern="**/*.json",
            source_name="archive.zip"
        )
        db.session.add(stub_job)
        
        for i in range(3):
            match_file = ExtractedFile(
                job_id="123",
                full_path=f"archive.zip/file_{i}.json",
                file_name=f"file_{i}.json",
                file_size=100,
                nesting_depth=0,
                source_archive_name="archive.zip"
            )
            db.session.add(match_file)
            
        db.session.commit()
    
    response =client.get('/extractions/123')
    assert response.status_code ==200
    
    data =response.get_json()
    assert data["status"]=="RUNNING"
    assert data["match_count"]==3


def test_get_status_not_found(client,app):
    response=client.get('/extractions/missing-uuid-456')
    assert response.status_code==404
    assert "not found" in response.get_json()["error"]
