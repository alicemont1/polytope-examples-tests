import base64
from io import BytesIO
from PIL import Image
import imagehash
from notebook_tester.config import IMG_COMPARE_THRESHOLD


def perceptual_hash(b64_png: str):
    data = base64.b64decode(b64_png)
    img = Image.open(BytesIO(data)).convert("RGB")
    return imagehash.phash(img)

def compare_images(nb1, nb2, checks1, checks2):
    paths_to_remove = []

    for (cell_idx1, out_idx1), (cell_idx2, out_idx2) in zip(checks1, checks2):
        try:
            # Get image data from first notebook
            png1 = nb1.cells[cell_idx1].outputs[out_idx1].data.get("image/png")
            if png1 is None:
                continue

            # Get image data from second notebook
            png2 = nb2.cells[cell_idx2].outputs[out_idx2].data.get("image/png")
            if png2 is None:
                continue

            # Join lines if image is stored as list of strings
            png1 = "".join(png1) if isinstance(png1, list) else png1
            png2 = "".join(png2) if isinstance(png2, list) else png2

            # Compare perceptual hash difference
            if perceptual_hash(png1) - perceptual_hash(png2) <= IMG_COMPARE_THRESHOLD:
                paths_to_remove.append(f"/cells/{cell_idx1}/outputs/{out_idx1}/data/image/png")

        except (IndexError, AttributeError, KeyError):
            # If any index is invalid or output structure is unexpected, skip
            continue

    return paths_to_remove
