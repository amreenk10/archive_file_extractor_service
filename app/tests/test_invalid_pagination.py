import pytest
from app.db import db
from app.models import ExtractionLog

def test_get_results_invalid_pagination(client, app):
    with app.app_context():
        stub_job = ExtractionLog(
            id="job-123",
            status="COMPLETED",
            pattern="*.json",
            source_name="archive.zip"
        )
        db.session.add(stub_job)
        db.session.commit()
    response =client.get('/extractions/job-123/results?limit=abc&offset=xyz')
    assert response.status_code ==200
    data=response.get_json()
    assert "results" in data
