import base64
from io import BytesIO
from PIL import Image
import imagehash
from notebook_tester.config import IMG_COMPARE_THRESHOLD


def perceptual_hash(b64_png: str):
    data = base64.b64decode(b64_png)
    img = Image.open(BytesIO(data)).convert("RGB")
    return imagehash.phash(img)

def compare_images(nb1, nb2, checks1, checks2, threshold=IMG_COMPARE_THRESHOLD):
    paths_to_remove = []

    for (cell_idx, out_idx1), (_, out_idx2) in zip(checks1, checks2):
        png1 = nb1.cells[cell_idx].outputs[out_idx1].data["image/png"]
        png2 = nb2.cells[cell_idx].outputs[out_idx2].data["image/png"]

        png1 = "".join(png1) if isinstance(png1, list) else png1
        png2 = "".join(png2) if isinstance(png2, list) else png2

        if perceptual_hash(png1) - perceptual_hash(png2) <= threshold:
            paths_to_remove.append(f"/cells/{cell_idx}/outputs/{out_idx1}/data/image/png")
            paths_to_remove.append(f"/cells/{cell_idx}/outputs/{out_idx2}/data/image/png")

    return paths_to_remove
