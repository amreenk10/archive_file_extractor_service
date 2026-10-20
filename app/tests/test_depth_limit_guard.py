from unittest.mock import patch, MagicMock
from app.services.extractor import archive_router

@patch('app.services.extractor.handle_zip')
@patch('app.services.extractor.handle_tar')
def test_extractor_depth_limit_guard(mock_handle_tar, mock_handle_zip):
    archive_router("bomb.zip","bomb.zip", 11,"*", "/tmp", [],"job-123",source_archive_name="bomb.zip")
    
    assert mock_handle_zip.called is False
    assert mock_handle_tar.called is False