import argparse
import re
import sys
from pathlib import Path
import win32com.client

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}

def get_folder(namespace, folder_path: str | None):
    # Default folder = inbox
    if not folder_path or folder_path.lower() == "inbox":
        return namespace.GetDefaultFolder(6)

    # Iterate thru subfolders if necessary
    parts = folder_path.split("/")
    if parts[0].lower() == "inbox":
        folder = namespace.GetDefaultFolder(6)
    else:
        folder = namespace.Folders[parts[0]]
    parts = parts[1:]
 
    for part in parts:
        folder = folder.Folders[part]
    return folder

def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "_", name)

def main():
    parser = argparse.ArgumentParser(
        description="Download image attachments from Outlook emails matching a subject."
    )
    parser.add_argument("subject",
                        help="Text to match against email subjects")
    parser.add_argument("-o", "--output", default="./downloaded_images",
                        help="Folder to save images into (default: ./downloaded_images)")
    parser.add_argument("--folder", default=None,
                        help="Outlook folder to search, e.g. 'Inbox' or 'Inbox/Archive' (default: Inbox)")
    parser.add_argument("--exact", action="store_true",
                        help="Require exact subject match instead of substring match")
    parser.add_argument("--min-size", type=int, default=0,
                        help="Skip image attachments smaller than this many bytes (e.g. to skip tiny signature logos)")
    args = parser.parse_args()

    out_dir = Path(args.output)
    # Make parent dirs as necessary, shouldn't fail if out dir exists
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Connecting to Outlook...")
    # Initialize Outlook connection
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    # Access a certain folder of that connection
    # 1: Archive
    # 3: Sent Items
    # 4: Deleted Items
    # 5: Drafts
    # 6: Inbox (default)
    try:
        folder = get_folder(namespace, args.folder)
        print(f"Resolved search folder: {folder.Name} (in store: {folder.Store.DisplayName})")
    except Exception as e:
        print(f"Could not find folder '{args.folder}': {e}")
        sys.exit(1)

    print(f"Searching folder '{folder.Name}' for subjects matching: \"{args.subject}\"")
 
    items = folder.Items
    target = args.subject if args.exact else args.subject.lower()
 
    matched_count = 0
    saved_count = 0
    skipped_small = 0
 
    for item in items:
        # We only want emails, MailItem class = 43
        # https://learn.microsoft.com/en-us/office/vba/api/outlook.olobjectclass
        try:
            if item.Class != 43:
                continue
            subject = item.Subject or ""
        except Exception:
            continue
 
        is_match = (subject == target) if args.exact else (target in subject.lower())
        if not is_match:
            continue
 
        matched_count += 1
        print(f"  Match: \"{subject}\" ({item.ReceivedTime})")
 
        for attachment in item.Attachments:
            fname = attachment.FileName
            ext = Path(fname).suffix.lower()
            if ext not in IMAGE_EXTENSIONS:
                continue
 
            if args.min_size and attachment.Size < args.min_size:
                skipped_small += 1
                continue
 
            safe_subject = sanitize_filename(subject)[:60]
            safe_fname = sanitize_filename(fname)
            # Prefix with a counter to avoid collisions when multiple emails
            # or attachments share the same filename.
            save_path = out_dir / f"{saved_count+1:03d}_{safe_subject}_{safe_fname}"
 
            attachment.SaveAsFile(str(save_path.resolve()))
            print(f"    Saved: {save_path.name}")
            saved_count += 1
 
    print(f"\nDone. {matched_count} matching email(s) found, {saved_count} image(s) saved to {out_dir.resolve()}")
    if skipped_small:
        print(f"({skipped_small} image(s) skipped for being under --min-size)")

if __name__ == "__main__":
    main()