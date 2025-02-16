import re
import os

def split_and_validate_anx(file_path, output_dir):
    with open(file_path, 'r') as file:
        content = file.read()

    # Regex to find headers with '*' and capture the message size
    pattern = re.compile(r'\*{4}(\d+)\*{4}')  # Matches ****0000000195****

    matches = list(pattern.finditer(content))
    
    for i, match in enumerate(matches):
        start = match.end()
        msg_size = int(match.group(1))  # Extract the message size from the header
        
        if i < len(matches) - 1:
            end = matches[i+1].start()
            message = content[start:end]
        else:
            message = content[start:]

        actual_size = len(message.encode('utf-8'))

        # Validate the message length
        if actual_size == msg_size:
            status = "valid"
        else:
            status = "bad"

        output_file = os.path.join(output_dir, f"message_{i+1}_{status}.txt")
        with open(output_file, 'w') as out:
            out.write(message)

        print(f"Message {i+1} written to {output_file} ({status})")

# Usage
split_and_validate_anx('path/to/your/anxfile.anx', 'path/to/output/directory')