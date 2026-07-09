import argparse
import csv
import re
from pathlib import Path

SECTION_RE = re.compile(r"^--- (.+?) ---\s*$", re.MULTILINE)
ASSIGNED_TO_RE = re.compile(r"([a-zA-Z]{1,2}\.[a-zA-Z]+)")
DEVICE_NAME_RE = re.compile(r"([A-Z]{3}-[0-9]{4}-[A-Z][0-9]{2})")
MODEL_RE = re.compile(r"((?:Latitude|Precision)\b[^\n]*)")
SERVICE_TAG_RE = re.compile(r"[A-Z0-9]{7}")


def parse_section(text: str) -> dict[str, str]:
    assigned = ASSIGNED_TO_RE.search(text)
    device = DEVICE_NAME_RE.search(text)
    model = MODEL_RE.search(text)
    service_tag = ""

    if model:
        tags = SERVICE_TAG_RE.findall(model.group(1))
        if tags:
            service_tag = tags[-1]

    return {
        "Assigned to": assigned.group(1) if assigned else "",
        "Device name": device.group(1) if device else "",
        "Model": model.group(1).strip() if model else "",
        "Service tag": service_tag,
    }


def parse_ocr_output(text: str) -> list[dict[str, str]]:
    rows = []
    matches = list(SECTION_RE.finditer(text))
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        rows.append(parse_section(text[start:end]))
    return rows


def main():
    parser = argparse.ArgumentParser(description="Parse OCR output into CSV.")
    parser.add_argument("input", nargs="?", default="output.txt", help="OCR text file")
    parser.add_argument("-o", "--output", default="output.csv", help="Output CSV path")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    rows = parse_ocr_output(text)

    fieldnames = ["Assigned to", "Device name", "Model", "Service tag"]
    with Path(args.output).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} row(s) to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
