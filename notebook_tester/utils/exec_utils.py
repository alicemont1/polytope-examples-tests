from nbconvert.preprocessors import ExecutePreprocessor
import nbformat
from notebook_tester.config import IS_LIVE_REQUEST


def override_variable_in_nb(nb, var_name, new_value):
    for cell in nb.cells:
        if cell.cell_type == "code" and f"{var_name} =" in cell.source:
            # Replace the assignment line
            lines = cell.source.splitlines()
            updated_lines = [
                f"{var_name} = {repr(new_value)}" if line.strip().startswith(f"{var_name} =") else line
                for line in lines
            ]
            cell.source = "\n".join(updated_lines)
    return nb

def execute_notebook(nb_object):
    override_variable_in_nb(nb_object, "LIVE_REQUEST", IS_LIVE_REQUEST)
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
    ep.preprocess(nb_object, {"metadata": {"path": '.'}})
    return nb_object

def inject_silence_stderr_cell(nb):
    """Insert a code cell to suppress stderr output."""
    patch_code = """
    import sys
    class DevNull:
        def write(self, msg): pass
        def flush(self): pass

    sys.stderr = DevNull()
    """
    silence_cell = nbformat.v4.new_code_cell(source=patch_code)
    nb.cells.insert(0, silence_cell)