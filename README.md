# Scripts
A repository of scripts used for my work, to learn new technologies, and for fun.
## [Image to `.csv`](./image_to_csv)
Uses OCR to turn images into text, then parses this text into useful `.csv`. Initially designed for more efficient IT inventory.
### Personal Notes
Applying [pytesseract](https://pypi.org/project/pytesseract/) + [PIL](https://pypi.org/project/pillow/) in an applied environment was quite an educational experience, especially when combining with user input. A variety of image types given by users prompted me to support more input file formats. I added more command line options ([argparser](https://docs.python.org/3/library/argparse.html)) because flexibility in usage was desired by coworkers using the script. Ultimately, the image &#8594; text &#8594; `.csv` logic was trivial, and the main challenge was creating the script in a robust and useful way.
## [Outlook Image Scraper](./outlook_image_scraper/)
Saves images from Outlook emails based on certain filters (e.g. subject line). Designed for use with image to `.csv`, creating an efficient, automated pipeline of gathering information across multiple offices &#8594; OCR into text &#8594; text into `.csv`.