import pytest
from unittest.mock import patch, MagicMock
from app.services.extractor import process_archive_job

@patch('app.services.extractor.archive_router')
@patch('app.services.extractor.os.makedirs')
@patch('app.services.extractor.db.session')
def test_process_job_failure_updates_database(mock_session, mock_makedirs, mock_router, app):
    mock_job=MagicMock()
    mock_session.get.return_value=mock_job
    mock_router.side_effect=Exception("Archive corruption block error")
    
    process_archive_job(app,"job-id","/tmp/bad.zip","bad.zip","*")
    
    assert mock_session.rollback.called
    assert mock_job.status=="FAILED"
    assert "corruption block" in mock_job.error_message
