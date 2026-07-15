# outlook_image_scraper

Download image attachments from Outlook emails whose subjects match a search string. Useful as a front end to `image_to_csv` when device screenshots arrive by email.

## Features

- **Subject search:** Match emails by subject substring (default) or exact match
- **Multi-account:** Search the default Outlook account or a named account/store
- **Folder paths:** Search Inbox or nested folders like `Inbox/Archive`
- **Image filtering:** Skip tiny attachments (e.g. signature logos) via `--min-size`
- **Deduplication:** Skip identical image content by default (SHA-256); keep them with `--keep-duplicates`

## Prerequisites

### Windows + Outlook

This script uses COM via `pywin32` and requires the desktop Outlook app on Windows with the target mailbox already configured.

### Python packages

```bash
pip install pywin32
```

## Quick start

```bash
# List connected accounts and top-level folders
python outlook_img_scraper.py --list-accounts

# Download images from matching emails into ./downloaded_images
python outlook_img_scraper.py "device inventory"
```

## `outlook_img_scraper.py`

Connects to Outlook, finds emails whose subjects match, and saves image attachments to a folder.

### Supported formats

`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp`

### Usage

```bash
python outlook_img_scraper.py [subject] [-o OUTPUT] [--folder FOLDER] [--account ACCOUNT]
                              [--exact] [--min-size BYTES] [--keep-duplicates] [--list-accounts]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `subject` | _(required)_ | Text to match against email subjects (not needed with `--list-accounts`) |
| `-o`, `--output` | `./downloaded_images` | Folder to save images into |
| `--folder` | Inbox | Outlook folder path, e.g. `Inbox` or `Archive` |
| `--account` | Outlook default | Account/store name, e.g. `you@company.com` |
| `--exact` | off | Require exact subject match instead of substring |
| `--min-size` | `0` | Skip image attachments smaller than this many bytes |
| `--keep-duplicates` | off | Keep duplicate images (default: skip identical content) |
| `--list-accounts` | off | List connected accounts and top-level folders, then exit |

### Examples

```bash
# Substring match in the default Inbox
python outlook_img_scraper.py "inventory screenshot"

# Exact subject match, custom output folder
python outlook_img_scraper.py "Q2 Device Audit" --exact -o ./audit_imgs

# Search a specific account and folder; skip tiny logos
python outlook_img_scraper.py "asset tag" --account "you@company.com" --folder Inbox --min-size 5000

# Keep duplicate images instead of skipping them
python outlook_img_scraper.py "asset tag" --keep-duplicates
```

Saved files are named like `001_Subject_snippet_originalname.png` (counter + sanitized subject + original filename) to avoid collisions.

By default, after each save the file is hashed; if that content was already seen in this run, the copy is deleted and counted as a skipped duplicate.

## Typical workflow

1. Run `--list-accounts` if you need the exact account or folder name.
2. Run `outlook_img_scraper.py` with a subject match to download images.
3. Optionally feed the output folder into `../image_to_csv` for OCR → CSV.

## Output files

Downloaded images are local working files (see `.gitignore` if present). Keep mailbox data and scraped images out of the repo; only the script is meant to be tracked.
