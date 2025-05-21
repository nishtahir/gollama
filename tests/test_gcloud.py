import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Adjust the import path based on your project structure
# This assumes 'src' is in PYTHONPATH or you're running tests from the project root.
from src.gollama.gcloud import upload_blob

class TestUploadBlob(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp()
        # Create a dummy file with some content in the temporary directory
        # We use NamedTemporaryFile to get a name, but then manage its lifecycle ourselves
        # by closing it and then using its name. This is safer for cross-platform compatibility.
        temp_file_descriptor, self.dummy_file_path = tempfile.mkstemp(dir=self.temp_dir)
        with os.fdopen(temp_file_descriptor, 'wb') as tmp:
            tmp.write(b"This is some dummy content for testing.")
        
        self.bucket_name = "test-bucket"
        self.blob_name = "test-blob.txt"

    def tearDown(self):
        # Remove the temporary directory and all its contents
        shutil.rmtree(self.temp_dir)

    @patch('src.gollama.gcloud.storage.Client')
    def test_upload_new_blob_no_force(self, mock_storage_client):
        """
        Test uploading a new blob when force is False.
        upload_from_file should be called.
        """
        # Configure the mock client, bucket, and blob
        mock_client_instance = mock_storage_client.return_value
        mock_bucket_instance = mock_client_instance.bucket.return_value
        mock_blob_instance = mock_bucket_instance.blob.return_value

        # Mock blob.exists() to return False (blob does not exist)
        mock_blob_instance.exists.return_value = False

        # Call the function to be tested
        upload_blob(self.dummy_file_path, self.bucket_name, self.blob_name, force=False)

        # Assertions
        mock_storage_client.assert_called_once()
        mock_client_instance.bucket.assert_called_once_with(self.bucket_name)
        mock_bucket_instance.blob.assert_called_once_with(self.blob_name)
        mock_blob_instance.exists.assert_called_once()
        
        # Check that upload_from_file was called
        # The actual file object passed to upload_from_file is wrapped by tqdm,
        # so we check that the method on the underlying mock_blob_instance was called.
        self.assertTrue(mock_blob_instance.upload_from_file.called, "upload_from_file should have been called for a new blob.")
        # More specific check if needed:
        # mock_blob_instance.upload_from_file.assert_called_once() 
        # We might need to be careful here if file_obj is wrapped. Let's check call count.
        self.assertEqual(mock_blob_instance.upload_from_file.call_count, 1)

    @patch('src.gollama.gcloud.storage.Client')
    def test_upload_existing_blob_no_force(self, mock_storage_client):
        """
        Test uploading an existing blob when force is False.
        upload_from_file should NOT be called.
        """
        mock_client_instance = mock_storage_client.return_value
        mock_bucket_instance = mock_client_instance.bucket.return_value
        mock_blob_instance = mock_bucket_instance.blob.return_value

        # Mock blob.exists() to return True (blob exists)
        mock_blob_instance.exists.return_value = True

        upload_blob(self.dummy_file_path, self.bucket_name, self.blob_name, force=False)

        mock_storage_client.assert_called_once()
        mock_client_instance.bucket.assert_called_once_with(self.bucket_name)
        mock_bucket_instance.blob.assert_called_once_with(self.blob_name)
        mock_blob_instance.exists.assert_called_once()
        
        # Check that upload_from_file was NOT called
        mock_blob_instance.upload_from_file.assert_not_called()

    @patch('src.gollama.gcloud.storage.Client')
    def test_upload_existing_blob_with_force(self, mock_storage_client):
        """
        Test uploading an existing blob when force is True.
        upload_from_file should be called.
        """
        mock_client_instance = mock_storage_client.return_value
        mock_bucket_instance = mock_client_instance.bucket.return_value
        mock_blob_instance = mock_bucket_instance.blob.return_value

        # Mock blob.exists() to return True (blob exists)
        mock_blob_instance.exists.return_value = True

        upload_blob(self.dummy_file_path, self.bucket_name, self.blob_name, force=True)

        mock_storage_client.assert_called_once()
        mock_client_instance.bucket.assert_called_once_with(self.bucket_name)
        mock_bucket_instance.blob.assert_called_once_with(self.blob_name)
        mock_blob_instance.exists.assert_called_once()
        
        # Check that upload_from_file was called
        mock_blob_instance.upload_from_file.assert_called_once()

    @patch('src.gollama.gcloud.storage.Client')
    def test_upload_new_blob_with_force(self, mock_storage_client):
        """
        Test uploading a new blob when force is True.
        upload_from_file should be called.
        """
        mock_client_instance = mock_storage_client.return_value
        mock_bucket_instance = mock_client_instance.bucket.return_value
        mock_blob_instance = mock_bucket_instance.blob.return_value

        # Mock blob.exists() to return False (blob does not exist)
        mock_blob_instance.exists.return_value = False

        upload_blob(self.dummy_file_path, self.bucket_name, self.blob_name, force=True)

        mock_storage_client.assert_called_once()
        mock_client_instance.bucket.assert_called_once_with(self.bucket_name)
        mock_bucket_instance.blob.assert_called_once_with(self.blob_name)
        mock_blob_instance.exists.assert_called_once()
        
        # Check that upload_from_file was called
        mock_blob_instance.upload_from_file.assert_called_once()


if __name__ == '__main__':
    unittest.main()
