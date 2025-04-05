import json


class OllamaManifest:
    def __init__(self, json: dict):
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
    def from_path(path: str) -> "OllamaManifest":
        with open(path, "r") as f:
            return OllamaManifest(json.load(f))


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

        # we assume that model names with no slashes are
        # pulled from the ollama model registry
        if "/" not in name:
            name = f"registry.ollama.ai/library/{name}"

        return OllamaModel(name=name, version=version)

    @staticmethod
    def from_manifest_path(path: str) -> "OllamaModel":
        # models/manifests/registry.ollama.ai/library/smollm2/135m -> smollm2:135m
        name = path.split("/")[-2]
        version = path.split("/")[-1]
        return OllamaModel(name=name, version=version)
