import pytest
from app.services.extractor import process_archive_job

def test_process_job_with_duplicate_filenames_different_paths(mock_extraction_context, app):
    mocks = mock_extraction_context
    
    process_archive_job(app,"job-123","/tmp/archive.zip","archive.zip","*.json")
    
    assert mocks["session"].bulk_save_objects.call_count==1
    assert mocks["job"].status=="COMPLETED"

def test_process_job_duplicate_path_database_conflict(mock_extraction_context,app):
    mocks = mock_extraction_context
    
    process_archive_job(app,"job-555","/tmp/dup.zip","dup.zip","*.json")
    
    assert mocks["session"].rollback.called
    assert mocks["job"].status == "FAILED"
    assert "Unique constraint" in mocks["job"].error_message

