import subprocess
import requests
import nbformat
from notebook_tester.config import REPO_URL, SUBMODULE_PATH, REFERENCE_BRANCH
from pathlib import Path

def get_modified_notebooks():
    result = subprocess.run(
        ["git", "-C", SUBMODULE_PATH, "status", "--porcelain"],
        capture_output=True, check=True, text=True
    )

    notebooks = []
    for line in result.stdout.splitlines():
        status, path = line[:2], line[3:]
        if path.endswith(".ipynb"):
            parts = path.split('/', 2)  # Split into at most 3 parts
            cleaned_path = parts[2] if len(parts) > 2 else path
            notebooks.append(cleaned_path)

    return notebooks

def get_reference_nb_from_repo(notebook_path):
    raw_url = f"{REPO_URL}/raw/{REFERENCE_BRANCH}/{notebook_path}"
    response = requests.get(raw_url)
    response.raise_for_status()
    return nbformat.reads(response.text, as_version=4)


def get_all_notebooks():
    return [
        str(p.relative_to(SUBMODULE_PATH))
        for p in Path(SUBMODULE_PATH).rglob("*.ipynb")
    ]
