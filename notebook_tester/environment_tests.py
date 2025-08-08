import base64
from io import BytesIO

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import pytest
from PIL import Image
import imagehash
import requests
import subprocess


from pytest_notebook.diffing import diff_notebooks, filter_diff, diff_to_string

# ----------------------------
# Configuration
# ----------------------------
NOTEBOOKS = [
    'climate-dt/climate-dt-earthkit-example.ipynb',
]

BASE_IGNORES = (
    '/metadata/*',
    '/cells/*/metadata',
    '/cells/*/execution_count',
    '/cells/*/source',
    '/cells/*/outputs/*/execution_count',
    '/cells/*/outputs/*/data/text/html',
)

TAG_IGNORES = {
    "skip-text-plain": "/cells/{idx}/outputs/*/data/text/plain",
    "skip-outputs": "/cells/{idx}/outputs",
    "skip-image": "/cells/{idx}/outputs/*/data/image/png",
}

TAG_IMAGE_CHECKS = {"check-image"}

SUBMODULE_PATH = "test" #TODO rename to polytope-examples
REPO_URL = "https://github.com/alicemont1/test"

# ----------------------------
# Utility Functions
# ----------------------------

def get_modified_notebooks(submodule_path):
    """Returns list of uncommitted modified .ipynb files in the given submodule."""
    result = subprocess.run(
        ["git", "-C", submodule_path, "status", "--porcelain"],
        capture_output=True, check=True, text=True
    )

    notebooks = []
    for line in result.stdout.splitlines():
        status, path = line[:2], line[3:]
        if path.endswith(".ipynb"):
            notebooks.append(path)

    return notebooks


def perceptual_hash(b64_png: str):
    data = base64.b64decode(b64_png)
    img = Image.open(BytesIO(data)).convert("RGB")
    return imagehash.phash(img)


def analyze_tags(nb):
    ignore_paths = []
    image_checks = []

    for idx, cell in enumerate(nb.cells):
        tags = set(cell.metadata.get("tags", []))

        for tag, template in TAG_IGNORES.items():
            if tag in tags:
                ignore_paths.append(template.format(idx=idx))

        if TAG_IMAGE_CHECKS & tags:
            for output_idx, output in enumerate(cell.get("outputs", [])):
                if "image/png" in output.get("data", {}):
                    image_checks.append((idx, output_idx))

    return ignore_paths, image_checks

# def inject_silence_stderr_cell(nb):
#     """Insert a code cell to suppress stderr output."""
#     patch_code = """
#     LIVE_REQUEST = False
#     import sys
#     class DevNull:
#         def write(self, msg): pass
#         def flush(self): pass

#     sys.stderr = DevNull()
#     """
#     silence_cell = nbformat.v4.new_code_cell(source=patch_code)
#     nb.cells.insert(0, silence_cell)
    
def compare_images(nb1, nb2, checks1, checks2, threshold=1):
    paths_to_remove = []
    # import pdb; pdb.set_trace()

    for (cell_idx, out_idx1), (_, out_idx2) in zip(checks1, checks2):
        png1 = nb1.cells[cell_idx].outputs[out_idx1].data["image/png"]
        png2 = nb2.cells[cell_idx].outputs[out_idx2].data["image/png"]

        png1 = "".join(png1) if isinstance(png1, list) else png1
        png2 = "".join(png2) if isinstance(png2, list) else png2

        if perceptual_hash(png1) - perceptual_hash(png2) <= threshold:
            paths_to_remove.append(f"/cells/{cell_idx}/outputs/{out_idx1}/data/image/png")

    return paths_to_remove

def inject_variable_override_cell(nb, variable, value):
    """Inject a cell that overrides a variable at the top of the notebook."""
    patch_code = f"{variable} = {repr(value)}"
    override_cell = nbformat.v4.new_code_cell(source=patch_code)
    nb.cells.insert(0, override_cell)


def get_reference_nb_from_repo(notebook_path, branch="master"):
    raw_url = f"{REPO_URL}/{branch}/{notebook_path}"
    
    response = requests.get(raw_url)
    response.raise_for_status()  # Raises error if file not found or repo unreachable

    reference_nb_obj = nbformat.reads(response.text, as_version=4)
    return reference_nb_obj


def execute_notebook(nb_object, working_dir):
    """Execute a notebook and return the executed notebook object."""
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
    # import pdb;pdb.set_trace()
    ep.preprocess(nb_object, {"path": '.'}) # this is the repository path

    return nb_object



# ----------------------------
# Parametrized Test
# ----------------------------

@pytest.mark.parametrize("test_nb", NOTEBOOKS)
def test_notebook_vs_baseline(test_nb):

    notebook_path = SUBMODULE_PATH + '/' + test_nb

    # Get notebook objects
    with open(notebook_path) as f:
        test_nb_obj = nbformat.read(f, as_version=4)
    reference_nb_obj = get_reference_nb_from_repo(test_nb)

    # Execute both notebooks
    executed_test_nb = execute_notebook(test_nb_obj, notebook_path)
    executed_reference_nb = execute_notebook(reference_nb_obj, notebook_path)

    # Gather ignore paths from tags
    ignore_paths_reference_nb, image_checks_reference_nb = analyze_tags(executed_reference_nb)
    ignore_paths_test_nb, image_checks_test_nb = analyze_tags(executed_test_nb)

    # Diff the notebooks
    raw_diff = diff_notebooks(executed_reference_nb, executed_test_nb)

    # Filter base ignores + tag-based ignores
    all_ignores = list(BASE_IGNORES) + ignore_paths_reference_nb + ignore_paths_test_nb
    filtered_diff = filter_diff(raw_diff, remove_paths=all_ignores)

    # If still diff left, check image diffs perceptually
    if filtered_diff:
        if image_checks_reference_nb and image_checks_test_nb:
            perceptually_equal_paths = compare_images(
                executed_reference_nb, executed_test_nb, image_checks_reference_nb, image_checks_test_nb
            )
            filtered_diff = filter_diff(filtered_diff, remove_paths=perceptually_equal_paths)

    # If anything still differs, fail
    if filtered_diff:
        diff_str = diff_to_string(executed_test_nb, filtered_diff, use_git=True, use_diff=True, use_color=True)
        pytest.fail(diff_str)