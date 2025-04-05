import os

from google.cloud import storage
from tqdm import tqdm


def upload_blob(file_path: str, bucket_name: str, blob_name: str) -> None:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # take the file name from the blob name
    file_name = os.path.basename(blob_name)
    # remove the sha256- prefix
    if file_name.startswith("sha256-"):
        file_name = file_name.split("-")[1][:12]

    with open(file_path, "rb") as in_file:
        total_bytes = os.fstat(in_file.fileno()).st_size
        with tqdm.wrapattr(
            in_file,
            "read",
            total=total_bytes,
            miniters=1,
            desc=f"pushing {file_name}...",
        ) as file_obj:
            blob.upload_from_file(file_obj)


def download_blob(bucket_name: str, blob_name: str, file_path: str) -> None:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    if blob is None:
        raise ValueError(f"Blob {blob_name} not found in bucket {bucket_name}")

    size = blob.size
    # take the file name from the blob name
    file_name = os.path.basename(blob_name)
    # remove the sha256- prefix
    if file_name.startswith("sha256-"):
        file_name = file_name.split("-")[1][:12]

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as out_file:
        with tqdm.wrapattr(
            out_file,
            "write",
            total=size,
            miniters=1,
            desc=f"pulling {file_name}...",
        ) as file_obj:
            blob.download_to_file(file_obj)


def list_blobs(bucket_name: str, prefix: str) -> list[str]:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    return [blob.name for blob in blobs]


def blob_exists(bucket_name: str, blob_name: str) -> bool:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.exists()
