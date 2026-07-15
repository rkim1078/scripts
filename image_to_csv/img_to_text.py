import argparse
import sys
import re
from pathlib import Path
import pytesseract
from PIL import Image
from tqdm import tqdm

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}

def collect_imgs(inputs: list[str]) -> list[Path]:
    paths = []
    # Handles both cases of `input` being a list of *.IMAGE_EXTENSIONS and input being a dir
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            # Recursively append image file extensions to list
            paths.extend(f for f in p.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS)
        elif p.is_file():
            paths.append(p)
        else:
            print(f"Warning: '{item}' not found, skipping.")
    return paths

def ocr_image(path: Path, lang: str = "eng") -> str:
    with Image.open(path) as img:
        # Grayscale preprocessing
        img = img.convert("L")
        return pytesseract.image_to_string(img, lang=lang)

def main():
    parser = argparse.ArgumentParser(description="OCR images into a single text file.")
    # Example usage, given folder of imgs `./scans`:
    #   python image_to_text.py ./scans -o output.txt
    parser.add_argument("inputs", nargs="*", default=[Path(".\\imgs")],
                        help="Input multiple image files or a folder of images, defaults to \".\\imgs\"")
    parser.add_argument("-o", "--output", default="output.txt",
                        help="Output the text file path, defaults to \"output.txt\"")
    parser.add_argument("--lang", default="eng",
                        help="Tesseract OCR language code (default: eng)")
    parser.add_argument("--no-page-markers", action="store_true",
                        help="Don't insert '--- filename ---' headers between pages")
    args = parser.parse_args()

    images = collect_imgs(args.inputs)
    if not images:
        print("No images found, exiting")
        sys.exit(1)

    print(f"Found {len(images)} image(s).")
    results = []
    for path in tqdm(images, desc="OCR", unit="img"):
        try:
            text = ocr_image(path, lang=args.lang)
        except Exception as e:
            text = f"[ERROR reading {path.name}: {e}]"
            tqdm.write(f"  -> {text}")

        if args.no_page_markers:
            results.append(text)
        else:
            results.append(f"--- {path.name} ---\n{text}")

    out_path = Path(args.output)
    out_path.write_text("\n\n".join(results), encoding="utf-8")
    print(f"\nDone. Text written to {out_path.resolve()}")
 
 
if __name__ == "__main__":
    main()