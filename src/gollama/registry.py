import json
from datetime import datetime

from google.cloud.storage import Blob as GcloudBlob

import gollama.gcloud as gcloud


class Manifest:
    def __init__(self, bucket_name: str, blob: GcloudBlob, text: str):
        self.bucket_name = bucket_name
        self.blob = blob
        self.content = json.loads(text)

    @property
    def name(self) -> str:
        path: str = self.blob.name  # type: ignore
        path = path.removeprefix("models/manifests/")
        path = path.removeprefix("registry.ollama.ai/")
        path = path.removeprefix("library/")

        name, version = path.rsplit("/", 1)
        return f"{name}:{version}"

    @property
    def details(self) -> dict:
        return self.content

    @property
    def modified(self) -> datetime:
        # remove timezone info for timeago
        return self.blob.updated.replace(tzinfo=None)  # type: ignore

    @property
    def size(self) -> int:
        return sum(layer["size"] for layer in self.content["layers"])

    def __str__(self):
        return f"Manifest(blob={self.blob.name})"

    def __repr__(self):
        return self.__str__()


class Blob:
    def __init__(self, blob: GcloudBlob):
        self.blob = blob

    def __str__(self):
        return f"Blob(blob={self.blob.name})"

    def __repr__(self):
        return self.__str__()


class GcloudRegistry:
    def __init__(self, manifests: list[Manifest], blobs: list[Blob]):
        self._manifests = manifests
        self._blobs = blobs

    @property
    def manifests(self) -> list[Manifest]:
        return self._manifests

    @property
    def blobs(self) -> list[Blob]:
        return self._blobs

    def has_blob(self, path: str) -> bool:
        return any(blob.blob.name == path for blob in self.blobs)

    def __str__(self):
        return f"GcloudRegistry(manifests={self.manifests}, blobs={self.blobs})"

    def __repr__(self):
        return self.__str__()


def create_registry(bucket_name: str) -> GcloudRegistry:
    manifest_blobs = gcloud.list_blobs(bucket_name, "models/manifests")
    contents = map(lambda blob: blob.download_as_text(), manifest_blobs)

    iterator = zip(manifest_blobs, contents)
    manifests = [Manifest(bucket_name, blob, content) for blob, content in iterator]

    blobs = [Blob(blob) for blob in gcloud.list_blobs(bucket_name, "models/blobs")]
    return GcloudRegistry(manifests, blobs)
