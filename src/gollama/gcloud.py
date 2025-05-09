import os

from google.cloud import storage
from google.cloud.storage import Blob
from tqdm import tqdm


def upload_blob(file_path: str, bucket_name: str, blob_name: str, force: bool = False) -> None:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    file_name = os.path.basename(blob_name)
    if file_name.startswith("sha256-"):
        file_name = file_name.split("-")[1][:12]

    with open(file_path, "rb") as in_file:
        total_bytes = os.fstat(in_file.fileno()).st_size

        if blob.exists() and not force:
            desc = f"skipping {file_name}"
            with tqdm(total=total_bytes, desc=desc) as pbar:
                pbar.update(total_bytes)
            return

        desc = f"pushing {file_name}..."
        with tqdm.wrapattr(in_file, "read", total=total_bytes, miniters=1, desc=desc) as file_obj:
            blob.upload_from_file(file_obj)


def download_blob(bucket_name: str, blob_name: str, file_path: str, force: bool = False) -> None:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    if blob is None:
        raise ValueError(f"Blob {blob_name} not found in bucket {bucket_name}")

    size = blob.size
    file_name = os.path.basename(blob_name)
    if file_name.startswith("sha256-"):
        file_name = file_name.split("-")[1][:12]

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as out_file:
        if os.path.exists(file_path) and not force:
            desc = f"skipping {file_name}"
            with tqdm(total=size, desc=desc) as pbar:
                pbar.update(size)
            return

        desc = f"pulling {file_name}..."
        with tqdm.wrapattr(out_file, "write", total=size, miniters=1, desc=desc) as file_obj:
            blob.download_to_file(file_obj)


def list_blobs(bucket_name: str, prefix: str) -> list[Blob]:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    return [blob for blob in blobs]


def delete_blob(bucket_name: str, blob_name: str) -> None:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()


def read_blob(bucket_name: str, blob_name: str) -> str:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_string().decode("utf-8")
