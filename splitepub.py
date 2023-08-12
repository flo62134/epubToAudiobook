import zipfile
import os
import xml.etree.ElementTree as ET


def extract_epub_pages(epub_file):
    with zipfile.ZipFile(epub_file, 'r') as z:
        z.extractall('./epub_files')


# Execute the function
extract_epub_pages('./ebook.epub')
