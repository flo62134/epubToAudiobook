import os

def regroup_pages():
    directory = "pages_text"
    output_directory = "pages_text_grouped"

    # Step 1: List all the files in the directory `pages_text`
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # Step 2: Sort them based on their naming pattern
    files.sort(key=lambda x: (x.split('_part')[1], int(x.split('_part')[0])))

    # Ensure output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for i, file in enumerate(files):
        with open(os.path.join(directory, file), 'r') as f:
            content = f.read()

        # Step 3: Check if the file ends with a period punctuation mark
        if not content.strip(' ').endswith('.'):
            # Step 4: Check if the next file has the same suffix and transfer content
            if i < len(files) - 1 and files[i + 1].split('_')[1] == file.split('_')[1]:
                with open(os.path.join(directory, files[i + 1]), 'r') as next_f:
                    next_content = next_f.read()

                # Split the next file's content at the first period punctuation mark
                first_part, _, rest = next_content.partition('.')
                content += first_part + '.'

                # Update the next file's content
                with open(os.path.join(directory, files[i + 1]), 'w') as next_f:
                    next_f.write(rest)

        # Step 5: Save the modified files in the directory `pages_text_grouped` with the same filenames
        with open(os.path.join(output_directory, file), 'w') as f:
            f.write(content)

    print('Files have been regrouped and saved in', output_directory)
