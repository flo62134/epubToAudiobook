import os
import re


def is_roman_numeral(s):
    # Regular expression for validating a Roman numeral
    pattern = '^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$'
    return bool(re.match(pattern, s))


def split_into_pages():
    epub_dir = "./epub_files/text/"

    # Get list of all html files in the directory
    html_files = [f for f in os.listdir(epub_dir) if f.endswith(".html")]

    # Directory for saving the files
    output_dir = "./pages_html/"

    # Ensure the directory exists; if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    all_output_files = []

    for html_file in html_files:
        with open(epub_dir + html_file, "r", encoding="utf-8") as file:
            content = file.read()

        # Splitting the content based on the specified pattern
        split_pattern = r'epub:type="pagebreak" id="pg'
        splits = content.split(split_pattern)

        # Extracting the IDs for file names
        file_ids = []
        for split in splits[1:]:  # skipping the first one as it won't have an ID
            # Extracting the potential ID
            potential_id = "".join([char for char in split[:10] if char.isdigit()])

            # Check if the ID is not a roman numeral
            if not is_roman_numeral(potential_id):
                file_ids.append(potential_id)

        # Writing the split contents to individual files
        for i, file_id in enumerate(file_ids):
            with open(output_dir + file_id + '_' + html_file.replace('.html', ''), "w", encoding="utf-8") as out_file:
                # Adding the split pattern back to the content except for the last file
                if i != len(file_ids) - 1:
                    out_file.write(splits[i + 1] + split_pattern + file_id)
                else:
                    # For the last file, we add the remaining content without adding the split pattern back
                    out_file.write(splits[i + 1])

        # Appending the output file paths
        all_output_files.extend([output_dir + file_id + ".html" for file_id in file_ids])


# For testing purposes
if __name__ == "__main__":
    split_into_pages()
