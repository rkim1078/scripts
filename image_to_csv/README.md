# image_to_text

Two small scripts for turning scanned device screenshots into structured CSV data:

1. **`img_to_text.py`** — OCR one or more images into a single text file.
2. **`parse_ocr_output.py`** — Parse that text file and extract device inventory fields into CSV.

## Features
- **Image to text:** Convert images into raw text using [TesseractOCR](https://github.com/tesseract-ocr/tesseract)
- **Text to `.csv`:** Regex parsing into .csv, initially designed for IT inventory purposes
- **Flexible inputs:** Supports 7 common image file formats, accepts list of files or directory

## Prerequisites

### Python packages

```bash
pip install pytesseract pillow
```

### Tesseract OCR (system install)

This project uses [Tesseract](https://github.com/tesseract-ocr/tesseract) via `pytesseract`. Install it separately:

- **Windows:** Download the installer from the [UB Mannheim builds](https://github.com/UB-Mannheim/tesseract/wiki) <!--and add the install directory to your `PATH` (e.g. `C:\Program Files\Tesseract-OCR`).-->
- **macOS:** `brew install tesseract`
- **Linux:** `sudo apt install tesseract-ocr` (Debian/Ubuntu)

<!-- If Tesseract is not on your `PATH`, set the executable path in code or the environment before running:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
``` -->

## Quick start

```bash
# Put images in ./imgs (or pass paths explicitly)
python img_to_text.py ./imgs -o output.txt

# Parse OCR output into CSV
python parse_ocr_output.py output.txt -o output.csv
```

## `img_to_text.py`

Runs OCR on image files and writes all extracted text to one output file.

### Supported formats

`.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.bmp`, `.webp`

### Usage

```bash
python img_to_text.py [inputs...] [-o OUTPUT] [--lang LANG] [--no-page-markers]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `inputs` | `./imgs` | One or more image files or directories |
| `-o`, `--output` | `output.txt` | Output text file path |
| `--lang` | `eng` | Tesseract language code (e.g. `eng`, `spa`) |
| `--no-page-markers` | off | Omit `--- filename ---` headers between images |

### Examples

```bash
# OCR everything in the default ./imgs folder
python img_to_text.py

# OCR specific files
python img_to_text.py scan1.png scan2.jpg -o results.txt

# OCR a folder of images in Spanish
python img_to_text.py ./scans --lang spa -o output.txt
```

Images are converted to grayscale before OCR. By default, each image's text is separated with a header like:

```
--- screenshot.png ---
<extracted text>
```

These headers are required for the parser script.

**Note:** When given a directory, only files directly in that folder are processed (not subfolders).

## `parse_ocr_output.py`

Reads OCR output produced by `img_to_text.py` and writes a CSV with these columns:

| Column | Source |
|--------|--------|
| Assigned to | Name pattern like `J.Smith` |
| Device name | Pattern like `ABC-1234-X01` |
| Model | Dell/Latitude/Precision model line |
| Service tag | 7-character alphanumeric tag from the model line |

### Usage

```bash
python parse_ocr_output.py [input] [-o OUTPUT]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `input` | `output.txt` | OCR text file to parse |
| `-o`, `--output` | `output.csv` | Output CSV path |

The script warns about empty cells that may need manual correction after OCR.

### Example

```bash
python parse_ocr_output.py output.txt -o devices.csv
```

## Typical workflow

1. Save device screenshots as images in `imgs/`.
2. Run `img_to_text.py` to produce `output.txt`.
3. Review `output.txt` for OCR errors; fix obvious mistakes if needed.
4. Run `parse_ocr_output.py` to generate `output.csv`.
5. Open the CSV and fill in any rows flagged with empty fields.

## Output files

Generated images, text, and CSV files are gitignored (see `.gitignore`). Keep inputs and outputs local; only the scripts are tracked in the repo.
