import os
from typing import Annotated

import timeago
import typer
from rich.console import Console
from rich.table import Table
from typer import Typer

import gollama.gcloud as gcloud
from gollama.model import OllamaManifest, OllamaModel
from gollama.registry import create_registry
from gollama.utils import human_readable_size

app = Typer(no_args_is_help=True)


@app.command("push", help="Push a model to a storage bucket")
def push(
    *,
    bucket_name: Annotated[str, typer.Option(envvar="GCS_BUCKET_NAME")],
    model: Annotated[str, typer.Argument(help="Model to push")],
    ollama_home: Annotated[str, typer.Option(envvar="OLLAMA_HOME")] = "~/.ollama",
    force: Annotated[bool, typer.Option(is_flag=True)] = False,
):
    ollama_home = os.path.expanduser(ollama_home)
    manifests_dir = os.path.join("models", "manifests")
    blobs_dir = os.path.join("models", "blobs")

    ollama_model = OllamaModel.from_name(model)
    manifest_path = os.path.join(manifests_dir, ollama_model.name, ollama_model.version)

    abs_manifest_path = os.path.join(ollama_home, manifest_path)
    manifest = OllamaManifest.from_path(abs_manifest_path)

    print("pushing manifest")
    gcloud.upload_blob(abs_manifest_path, bucket_name, manifest_path, force=force)

    blobs = manifest.blobs()

    for blob in blobs:
        blob_name = blob.replace(":", "-")
        blob_path = os.path.join(blobs_dir, blob_name)
        abs_blob_path = os.path.join(ollama_home, blob_path)
        gcloud.upload_blob(abs_blob_path, bucket_name, blob_path, force=force)

    print("success")


@app.command("list", help="List models in a storage bucket")
def list(
    *,
    bucket_name: Annotated[str, typer.Option(envvar="GCS_BUCKET_NAME")],
):
    registry = create_registry(bucket_name)

    table = Table(box=None)
    table.add_column("NAME")
    table.add_column("SIZE")
    table.add_column("MODIFIED")
    for manifest in registry.manifests:
        table.add_row(
            manifest.name,
            human_readable_size(manifest.size),
            timeago.format(manifest.modified),
        )

    console = Console()
    console.print(table)


@app.command("pull", help="Pull a model from a storage bucket")
def pull(
    *,
    bucket_name: Annotated[str, typer.Option(envvar="GCS_BUCKET_NAME")],
    model: Annotated[str, typer.Argument(help="Model to pull")],
    ollama_home: Annotated[str, typer.Option(envvar="OLLAMA_HOME")] = "~/.ollama",
    force: Annotated[bool, typer.Option(is_flag=True)] = False,
):
    ollama_home = os.path.expanduser(ollama_home)
    manifests_dir = os.path.join("models", "manifests")
    blobs_dir = os.path.join("models", "blobs")

    ollama_model = OllamaModel.from_name(model)
    manifest_path = os.path.join(manifests_dir, ollama_model.name, ollama_model.version)
    abs_manifest_path = os.path.join(ollama_home, manifest_path)

    print("pulling manifest")
    # We always download the manifest, even if it already exists.
    # This is because the manifest is a JSON file, and it may have changed.
    gcloud.download_blob(bucket_name, manifest_path, abs_manifest_path, force=True)
    manifest = OllamaManifest.from_path(abs_manifest_path)

    blobs = manifest.blobs()
    for blob in blobs:
        blob_name = blob.replace(":", "-")
        blob_path = os.path.join(blobs_dir, blob_name)
        abs_blob_path = os.path.join(ollama_home, blob_path)
        gcloud.download_blob(bucket_name, blob_path, abs_blob_path, force=force)


@app.command("rm", help="Remove a model from a storage bucket")
def rm(
    *,
    model: Annotated[str, typer.Argument(help="Model to remove")],
    bucket_name: Annotated[str, typer.Option(envvar="GCS_BUCKET_NAME")],
    ollama_home: Annotated[str, typer.Option(envvar="OLLAMA_HOME")] = "~/.ollama",
):
    ollama_home = os.path.expanduser(ollama_home)
    manifests_dir = os.path.join("models", "manifests")
    blobs_dir = os.path.join("models", "blobs")

    ollama_model = OllamaModel.from_name(model)
    manifest_path = os.path.join(manifests_dir, ollama_model.name, ollama_model.version)
    manifest_content = gcloud.read_blob(bucket_name, manifest_path)
    manifest = OllamaManifest.from_str(manifest_content)

    blobs = manifest.blobs()
    for blob in blobs:
        blob_name = blob.replace(":", "-")
        blob_path = os.path.join(blobs_dir, blob_name)
        gcloud.delete_blob(bucket_name, blob_path)

    gcloud.delete_blob(bucket_name, manifest_path)
    print(f"deleted '{model}'")


if __name__ == "__main__":
    app()
