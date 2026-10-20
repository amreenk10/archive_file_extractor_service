from unittest.mock import patch
from app.services.extractor import archive_router

@patch('app.services.extractor.handle_zip')
@patch('app.services.extractor.handle_tar')
def test_archive_router_tar_vs_zip(mock_handle_tar, mock_handle_zip):
    archive_router(
        "data.zip","data.zip", 0, "*","/tmp",[], "job-123", 
        source_archive_name="data.zip"
    )
    assert mock_handle_zip.called is True
    assert mock_handle_tar.called is False

    mock_handle_zip.reset_mock()
    mock_handle_tar.reset_mock()
    archive_router("data.tar.gz","data.tar.gz", 0, "*", "/tmp",[],"job-123",source_archive_name="data.tar.gz")
    assert mock_handle_zip.called is False
    assert mock_handle_tar.called is True
