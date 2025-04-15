import json
from typing import Any


class OllamaManifest:
    def __init__(self, json: dict[str, Any]):
        self.json = json

    def config(self) -> dict:
        return self.json["config"]

    def layers(self) -> list[dict]:
        return self.json["layers"]

    def blobs(self) -> list[str]:
        blobs = []
        blobs.append(self.config()["digest"])

        for layer in self.layers():
            blobs.append(layer["digest"])
        return blobs

    @staticmethod
    def from_str(content: str) -> "OllamaManifest":
        return OllamaManifest(json.loads(content))

    @staticmethod
    def from_path(path: str) -> "OllamaManifest":
        with open(path, "r") as f:
            return OllamaManifest.from_str(f.read())


class OllamaModel:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version

    def __str__(self):
        return f"{self.name}:{self.version}"

    @staticmethod
    def from_name(model_name: str) -> "OllamaModel":
        if ":" not in model_name:
            model_name = f"{model_name}:latest"

        name, version = model_name.split(":")
        if not _uses_custom_registry(name):
            # We need to determin if it's from the
            # ollama model registry. if there's no '/'
            # then the package is stored in the library
            # otherwise it's stored in the custom registry
            if "/" not in name:
                name = f"library/{name}"

            # now we can construct the fully qualified name
            # using the ollama model registry prefix
            name = f"registry.ollama.ai/{name}"

        return OllamaModel(name=name, version=version)

    @staticmethod
    def from_manifest_path(path: str) -> "OllamaModel":
        # models/manifests/registry.ollama.ai/library/smollm2/135m -> smollm2:135m
        name = path.split("/")[-2]
        version = path.split("/")[-1]
        return OllamaModel(name=name, version=version)


def _uses_custom_registry(image_name: str) -> bool:
    # We're borrowing some logic from docker to determine if the
    # image is from a custom registry. My understanding is that
    # docker assumes an image is from a custom registry if the
    # segment before the first '/' contains a '.' (dot), a ':' (colon),
    # or equals "localhost". Otherwise, it defaults to Docker Hub.
    parts = image_name.split("/", 1)

    if len(parts) == 1:
        return False

    registry_candidate = parts[0]

    return (
        ("." in registry_candidate)
        or (":" in registry_candidate)
        or (registry_candidate == "localhost")
    )
