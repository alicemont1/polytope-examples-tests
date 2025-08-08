import pytest
import nbformat
from pathlib import Path

from notebook_tester.config import BASE_IGNORES, SUBMODULE_PATH, TEST_MODIFIED_NOTEBOOKS, NOTEBOOKS
from notebook_tester.utils.exec_utils import execute_notebook
from notebook_tester.utils.diff_utils import run_diff
from notebook_tester.utils.image_utils import compare_images
from notebook_tester.utils.repo_utils import get_reference_nb_from_repo, get_modified_notebooks

from notebook_tester.utils.tag_utils import analyze_tags



@pytest.mark.parametrize("test_nb", get_modified_notebooks() if TEST_MODIFIED_NOTEBOOKS else NOTEBOOKS)
def test_notebook_vs_baseline(test_nb):
    parts = test_nb.split('/', 2)  # Split into at most 3 parts
    cleaned_path = parts[2] if len(parts) > 2 else test_nb
    notebook_path = f"{SUBMODULE_PATH}/{cleaned_path}"

    with open(notebook_path) as f:
        test_nb_obj = nbformat.read(f, as_version=4)

    reference_nb_obj = get_reference_nb_from_repo(cleaned_path)

    executed_test_nb = execute_notebook(test_nb_obj)
    executed_reference_nb = execute_notebook(reference_nb_obj)

    ignore_paths_ref, image_checks_ref = analyze_tags(executed_reference_nb)
    ignore_paths_test, image_checks_test = analyze_tags(executed_test_nb)

    all_ignores = list(BASE_IGNORES) + ignore_paths_ref + ignore_paths_test

    perceptual_ignores = compare_images(
        executed_reference_nb, executed_test_nb, image_checks_ref, image_checks_test
    ) if image_checks_ref and image_checks_test else []

    
    filtered_diff, diff_str = run_diff(
        executed_reference_nb, executed_test_nb,
        ignore_paths=all_ignores,
        image_diff_paths=perceptual_ignores
    )

    if filtered_diff:
        pytest.fail(diff_str)
