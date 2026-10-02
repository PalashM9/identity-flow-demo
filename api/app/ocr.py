from pathlib import Path
import pytesseract
from PIL import Image


def read_identity_document(image_path: str) -> str:
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Document image does not exist: {image_path}")

    image = Image.open(path)
    return pytesseract.image_to_string(image, lang="eng").strip()