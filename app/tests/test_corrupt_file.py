import pytest
from app.services.extractor import process_archive_job

def test_process_job_handles_corrupt_files_gracefully(app, mock_extraction_context):
    mocks=mock_extraction_context
    mocks["router"].side_effect = Exception("Bad zip file binaries or archive corruption")

    process_archive_job(app,"job-999","/dev/null","corrupt.zip", "*")

    assert mocks["job"].status=="FAILED"
    assert mocks["job"].error_message is not None

