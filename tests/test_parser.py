import os

from gollama.model import OllamaManifest, OllamaModel
from gollama.utils import __PROJECT_ROOT__


def test_parse_ollama_model_from_name(snapshot):
    names = [
        "gemma3",
        "gemma3:12b",
        "microsoft/phi-4:latest",
        "gemma3:4b",
        "hf.co/lmstudio-community/zeta-GGUF:Q4_K_M",
        "llama3.1:8b",
        "qwen2.5-coder:1.5b-base",
        "nomic-embed-text:latest",
    ]

    models = list(map(OllamaModel.from_name, names))
    snapshot.assert_match(models)


def test_parse_ollama_manifest_from_path(snapshot):
    manifest = OllamaManifest.from_path(
        os.path.join(
            __PROJECT_ROOT__,
            "tests/fixtures/microsoft-phi-4-latest",
        )
    )
    snapshot.assert_match(manifest)


def test_parse_ollama_manifest_blobs(snapshot):
    manifest = OllamaManifest.from_path(
        os.path.join(
            __PROJECT_ROOT__,
            "tests/fixtures/microsoft-phi-4-latest",
        )
    )
    blobs = manifest.blobs()
    snapshot.assert_match(blobs)
