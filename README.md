# gollama (google cloud storage for ollama)

User's working on their own models may want to store their own models privately. While `ollama` conforms to the OCI specification,
it's not possible to push/pull models from a private registry (see [ollama/ollama#7244](https://github.com/ollama/ollama/issues/7244)).

This utility provides a simple tool for managing Ollama Models stored in a [Google Cloud Storage](https://cloud.google.com/storage) bucket using a familiar CLI Interface.

## Requirements

- Python 3.11+
- gcloud cli ([installation guide](https://cloud.google.com/sdk/docs/install))

## Setup

Clone the repository.

````bash
git clone https://github.com/nishtahir/gollama.git
cd gollama

Create a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
````

Install uv and sync the dependencies.

```bash
pip install uv
uv sync
```

## Usage

```

 Usage: gollama [OPTIONS] COMMAND [ARGS]...

╭─ Options ──────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.    │
│ --show-completion             Show completion for the current shell, to    │
│                               copy it or customize the installation.       │
│ --help                        Show this message and exit.                  │
╰────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────╮
│ push   Push a model to a storage bucket                                    │
│ list   List models in a storage bucket                                     │
│ pull   Pull a model from a storage bucket                                  │
╰────────────────────────────────────────────────────────────────────────────╯

```

### Push a model to a storage bucket

```bash
gollama push <model>
```

### List models in a storage bucket

```bash
gollama list
```

### Pull a model from a storage bucket

```bash
gollama pull <model>
```

## Authentication

This uses the google cloud sdk so you need to authenticate with `gcloud` before using the tool.

```bash
gcloud login
gcloud auth application-default login
```

It assumes a default project is set and a storage bucket is already created.

```bash
gcloud config set project <project-id>
gcloud storage buckets create gs://<bucket-name>
```
