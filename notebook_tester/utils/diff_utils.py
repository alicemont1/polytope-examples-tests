from pytest_notebook.diffing import diff_notebooks, filter_diff, diff_to_string

def run_diff(reference_nb, test_nb, ignore_paths, image_diff_paths=None):
    raw_diff = diff_notebooks(reference_nb, test_nb)
    filtered = filter_diff(raw_diff, remove_paths=ignore_paths)

    if filtered and image_diff_paths:
        filtered = filter_diff(filtered, remove_paths=image_diff_paths)

    return filtered, diff_to_string(test_nb, filtered, use_git=True, use_diff=True, use_color=True)
