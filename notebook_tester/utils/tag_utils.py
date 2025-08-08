from notebook_tester.config import TAG_IGNORES, TAG_IMAGE_CHECKS

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
