import os
import tempfile
import shutil
import pytest

# Adjust the import path based on your project structure
# This assumes 'src' is in PYTHONPATH or you're running tests from the project root.
from src.gollama.gcloud import upload_blob

# Common constants for tests
BUCKET_NAME = "test-bucket"
BLOB_NAME = "test-blob.txt"

@pytest.fixture
def dummy_file_path_fixture():
    """
    Pytest fixture to create a temporary directory and a dummy file with content.
    Yields the path to the dummy file and cleans up the directory afterwards.
    """
    temp_dir = tempfile.mkdtemp()
    temp_file_descriptor, dummy_file_path = tempfile.mkstemp(dir=temp_dir)
    with os.fdopen(temp_file_descriptor, 'wb') as tmp:
        tmp.write(b"This is some dummy content for testing.")
    
    yield dummy_file_path  # Provide the path to the test

    # Teardown: Remove the temporary directory and all its contents
    shutil.rmtree(temp_dir)


def test_upload_new_blob_no_force(dummy_file_path_fixture, mocker):
    """
    Test uploading a new blob when force is False.
    upload_from_file should be called.
    """
    mock_storage_client = mocker.patch('src.gollama.gcloud.storage.Client')
    
    # Configure the mock client, bucket, and blob
    mock_client_instance = mock_storage_client.return_value
    mock_bucket_instance = mock_client_instance.bucket.return_value
    mock_blob_instance = mock_bucket_instance.blob.return_value

    # Mock blob.exists() to return False (blob does not exist)
    mock_blob_instance.exists.return_value = False

    # Call the function to be tested
    upload_blob(dummy_file_path_fixture, BUCKET_NAME, BLOB_NAME, force=False)

    # Assertions
    assert mock_storage_client.call_count == 1
    mock_client_instance.bucket.assert_called_once_with(BUCKET_NAME)
    mock_bucket_instance.blob.assert_called_once_with(BLOB_NAME)
    assert mock_blob_instance.exists.call_count == 1
    
    assert mock_blob_instance.upload_from_file.called, "upload_from_file should have been called for a new blob."
    assert mock_blob_instance.upload_from_file.call_count == 1


def test_upload_existing_blob_no_force(dummy_file_path_fixture, mocker):
    """
    Test uploading an existing blob when force is False.
    upload_from_file should NOT be called.
    """
    mock_storage_client = mocker.patch('src.gollama.gcloud.storage.Client')

    mock_client_instance = mock_storage_client.return_value
    mock_bucket_instance = mock_client_instance.bucket.return_value
    mock_blob_instance = mock_bucket_instance.blob.return_value

    # Mock blob.exists() to return True (blob exists)
    mock_blob_instance.exists.return_value = True

    upload_blob(dummy_file_path_fixture, BUCKET_NAME, BLOB_NAME, force=False)

    assert mock_storage_client.call_count == 1
    mock_client_instance.bucket.assert_called_once_with(BUCKET_NAME)
    mock_bucket_instance.blob.assert_called_once_with(BLOB_NAME)
    assert mock_blob_instance.exists.call_count == 1
    
    assert not mock_blob_instance.upload_from_file.called
    assert mock_blob_instance.upload_from_file.call_count == 0


def test_upload_existing_blob_with_force(dummy_file_path_fixture, mocker):
    """
    Test uploading an existing blob when force is True.
    upload_from_file should be called.
    """
    mock_storage_client = mocker.patch('src.gollama.gcloud.storage.Client')

    mock_client_instance = mock_storage_client.return_value
    mock_bucket_instance = mock_client_instance.bucket.return_value
    mock_blob_instance = mock_bucket_instance.blob.return_value

    # Mock blob.exists() to return True (blob exists)
    mock_blob_instance.exists.return_value = True

    upload_blob(dummy_file_path_fixture, BUCKET_NAME, BLOB_NAME, force=True)

    assert mock_storage_client.call_count == 1
    mock_client_instance.bucket.assert_called_once_with(BUCKET_NAME)
    mock_bucket_instance.blob.assert_called_once_with(BLOB_NAME)
    assert mock_blob_instance.exists.call_count == 1
    
    assert mock_blob_instance.upload_from_file.call_count == 1


def test_upload_new_blob_with_force(dummy_file_path_fixture, mocker):
    """
    Test uploading a new blob when force is True.
    upload_from_file should be called.
    """
    mock_storage_client = mocker.patch('src.gollama.gcloud.storage.Client')

    mock_client_instance = mock_storage_client.return_value
    mock_bucket_instance = mock_client_instance.bucket.return_value
    mock_blob_instance = mock_bucket_instance.blob.return_value

    # Mock blob.exists() to return False (blob does not exist)
    mock_blob_instance.exists.return_value = False

    upload_blob(dummy_file_path_fixture, BUCKET_NAME, BLOB_NAME, force=True)

    assert mock_storage_client.call_count == 1
    mock_client_instance.bucket.assert_called_once_with(BUCKET_NAME)
    mock_bucket_instance.blob.assert_called_once_with(BLOB_NAME)
    assert mock_blob_instance.exists.call_count == 1
    
    assert mock_blob_instance.upload_from_file.call_count == 1
