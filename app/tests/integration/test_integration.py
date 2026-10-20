import os
import pytest
from unittest.mock import patch
from app.services.extractor import process_archive_job

def test_full_extraction_pipeline_integration(client, app):
    test_file_path = "nested_sample.zip"

    if not os.path.exists(test_file_path):
        pytest.skip(f"Test archive '{test_file_path}' not found in root folder. Skipping integration test.")

    with patch('app.routes.submit.submit_extraction_task') as mock_submit:
        def inline_execution(*args, **kwargs):
            app_instance=kwargs.get("app")
            job_id=kwargs.get("job_id")
            saved_path= kwargs.get("upload_path")
            filename =kwargs.get("original_filename")
            pattern=kwargs.get("glob_pattern")
            
            
            process_archive_job(app,job_id, saved_path,filename,pattern)
            
        mock_submit.side_effect=inline_execution

        with open(test_file_path,"rb") as archive_file:
            data = {
                "archive": (archive_file, "nested_sample.zip"),
                "pattern": "**/*.json"
            }

            response=client.post('/extractions', data=data, content_type='multipart/form-data')
            assert response.status_code== 202
