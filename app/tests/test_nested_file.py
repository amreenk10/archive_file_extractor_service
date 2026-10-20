import os
import io
import zipfile
import pytest
from unittest.mock import patch, MagicMock
from app.services.zip_handler import handle_zip
from app.models import ExtractedFile

@patch('app.services.zip_handler.shutil.copyfileobj')
@patch('app.services.zip_handler.open', create=True)
def test_handle_zip_finds_nested_archives(mock_open, mock_copyfileobj):
    zip_buffer=io.BytesIO()
    with zipfile.ZipFile(zip_buffer,'w') as fake_zip:
        fake_zip.writestr("data/target.json", b"{}")
        fake_zip.writestr("nested/inner.zip", b"fake binary data")

    zip_buffer.seek(0)
    matches_found=[]
    mock_recursive_trigger=MagicMock()
    mock_file_handle=MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file_handle
    
    with patch('app.services.zip_handler.os.path.exists', return_value=True), \
         patch('app.services.zip_handler.os.remove') as mock_remove:
         
        handle_zip(
            file_path=zip_buffer,
            display_chain="outer.zip",
            depth=0,
            pattern="**/*.json",
            workspace_dir="/tmp/fake_dir",
            matches=matches_found,
            job_id="job-111",
            recursive_trigger=mock_recursive_trigger,
            source_archive_name="outer.zip"
        )

    assert len(matches_found)==1
    assert matches_found[0]["file_name"]=="target.json"
    assert mock_recursive_trigger.called is True
    assert mock_remove.called is True