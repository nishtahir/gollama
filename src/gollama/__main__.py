import os
from typing import Annotated

import typer
from typer import Typer

import gollama.gcloud as gcloud
from gollama.model import OllamaManifest, OllamaModel

app = Typer(no_args_is_help=True)


@app.command("push", help="Push a model to a storage bucket")
def push(
    *,
    model: Annotated[str, typer.Argument(help="Model to push")],
    ollama_home: Annotated[str, typer.Option(envvar="OLLAMA_HOME")] = "~/.ollama",
    bucket_name: Annotated[str, typer.Option(envvar="GCS_BUCKET_NAME")],
):
    ollama_home = os.path.expanduser(ollama_home)
    manifests_dir = os.path.join("models", "manifests")
    blobs_dir = os.path.join("models", "blobs")

    ollama_model = OllamaModel.from_name(model)
    manifest_path = os.path.join(manifests_dir, ollama_model.name, ollama_model.version)

    abs_manifest_path = os.path.join(ollama_home, manifest_path)
    manifest = OllamaManifest.from_path(abs_manifest_path)
    # upload the manifest

    print("pushing manifest")
    gcloud.upload_blob(abs_manifest_path, bucket_name, manifest_path)

    blobs = manifest.blobs()

    for blob in blobs:
        blob_name = blob.replace(":", "-")
        blob_path = os.path.join(blobs_dir, blob_name)
        abs_blob_path = os.path.join(ollama_home, blob_path)
        gcloud.upload_blob(abs_blob_path, bucket_name, blob_path)


@app.command("list", help="List models in a storage bucket")
def list(
    *,
    bucket_name: Annotated[str, typer.Option(envvar="GCS_BUCKET_NAME")],
):
    manifests_dir = os.path.join("models", "manifests")
    blobs = gcloud.list_blobs(bucket_name, manifests_dir)
    for manifest in blobs:
        model = OllamaModel.from_manifest_path(manifest)
        print(model)


@app.command("pull", help="Pull a model from a storage bucket")
def pull(
    *,
    model: Annotated[str, typer.Argument(help="Model to pull")],
    ollama_home: Annotated[str, typer.Option(envvar="OLLAMA_HOME")] = "~/.ollama",
    bucket_name: Annotated[str, typer.Option(envvar="GCS_BUCKET_NAME")],
):
    ollama_home = os.path.expanduser(ollama_home)
    manifests_dir = os.path.join("models", "manifests")
    blobs_dir = os.path.join("models", "blobs")

    # check if the model exists in the bucket
    ollama_model = OllamaModel.from_name(model)
    manifest_path = os.path.join(manifests_dir, ollama_model.name, ollama_model.version)
    abs_manifest_path = os.path.join(ollama_home, manifest_path)

    # download the manifest
    print("pulling manifest")
    gcloud.download_blob(bucket_name, manifest_path, abs_manifest_path)
    manifest = OllamaManifest.from_path(abs_manifest_path)

    # download the blobs
    blobs = manifest.blobs()
    for blob in blobs:
        blob_name = blob.replace(":", "-")
        blob_path = os.path.join(blobs_dir, blob_name)
        abs_blob_path = os.path.join(ollama_home, blob_path)
        gcloud.download_blob(bucket_name, blob_path, abs_blob_path)


if __name__ == "__main__":
    app()
