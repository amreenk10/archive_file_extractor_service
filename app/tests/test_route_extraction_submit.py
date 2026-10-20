import pytest
from io import BytesIO
from unittest.mock import patch

@patch('app.routes.submit.db.session')
@patch('app.routes.submit.submit_extraction_task')
def test_create_job_success(mock_submit_task,mock_db_session, client):
    data = {
        'archive': (BytesIO(b"fake zip binaries"),'sample.zip'),
        'pattern': '**/*.json'
    }
    response=client.post('/extractions',data=data,content_type='multipart/form-data')
    assert response.status_code==202
    assert "job_id" in response.get_json()
    assert mock_submit_task.called

def test_create_job_missing_payload_parameters(client):
    response=client.post('/extractions',data={})
    assert response.status_code==400
    assert "error" in response.get_json()
