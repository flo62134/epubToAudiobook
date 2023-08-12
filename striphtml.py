import os
import re


def remove_html_tags(data):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', data)


def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

        # Remove the doc-pagebreak pattern
        content = re.sub(r'<span epub:type="pagebreak" id="pg\d+', '', content)

        # Remove the doc-pagebreak pattern
        content = re.sub(r'^\d+" role="doc-pagebreak" aria-label="\d+" class="calibre"></span>', '', content)

        # Remove all HTML tags
        content = remove_html_tags(content)

        with open(output_path, 'w', encoding='utf-8') as out:
            out.write(content)


def strip_html():
    input_dir = './pages_html'
    output_dir = './pages_text'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        process_file(input_path, output_path)
