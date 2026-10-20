import pytest
from unittest.mock import patch
from app.services.extractor import archive_router

@patch('app.services.extractor.handle_zip')
def test_router_maps_zip_extensions(mock_handle_zip):
    archive_router("data.ZIP", "data.ZIP", 0,"*.csv","/tmp/dir", [], "job-123")
    assert mock_handle_zip.called

@patch('app.services.extractor.handle_zip')
@patch('app.services.extractor.handle_tar')
def test_router_blocks_malicious_nesting_bombs(mock_handle_tar, mock_handle_zip):
    archive_router("nested.zip","nested.zip", 6,"*.*","/tmp/dir",[],"job-789")
    assert not mock_handle_zip.called
    assert not mock_handle_tar.called
