import base64
import tempfile
from io import BytesIO
from pathlib import Path

import nbformat
import pytest
from PIL import Image
import imagehash

from pytest_notebook.nb_regression import NBRegressionFixture
from notebook_tester.config import BASE_IGNORES, NOTEBOOKS, SUBMODULE_PATH, IS_LIVE_REQUEST
from notebook_tester.utils.tag_utils import analyze_tags
from notebook_tester.utils.exec_utils import override_variable_in_nb, inject_silence_stderr_cell
from notebook_tester.utils.diff_utils import run_diff
from notebook_tester.utils.image_utils import compare_images


@pytest.mark.parametrize("test_nb", NOTEBOOKS)
def test_changed_notebook(test_nb, nb_regression: NBRegressionFixture):
    # Load and patch notebook
    parts = test_nb.split('/', 2)
    cleaned_path = parts[2] if len(parts) > 2 else test_nb
    notebook_path = f"{SUBMODULE_PATH}/{cleaned_path}"

    nb = nbformat.read(notebook_path, as_version=4)
    inject_silence_stderr_cell(nb)
    override_variable_in_nb(nb, "LIVE_REQUEST", IS_LIVE_REQUEST)

    # Analyze for tag-based ignore paths and image checks
    ignore_paths, _ = analyze_tags(nb)

    # Save modified notebook to temporary file
    with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False, mode="w") as tmp:
        nbformat.write(nb, tmp)
        patched_path = tmp.name

    # Setup regression execution
    nb_regression.exec_cwd = str(Path(notebook_path).parent)

    result = nb_regression.check(patched_path, raise_errors=False)

    _, image_checks_ref = analyze_tags(result.nb_final)
    _, image_checks_test = analyze_tags(result.nb_initial)

    perceptual_ignores = compare_images(
        result.nb_initial, result.nb_final, image_checks_ref, image_checks_test, threshold=4
    ) if image_checks_ref and image_checks_test else []
    
    filtered_diff, diff_str = run_diff(
        result.nb_final, result.nb_initial,
        ignore_paths=list(BASE_IGNORES),
        image_diff_paths=perceptual_ignores
    )

    if filtered_diff:
        pytest.fail(diff_str)
