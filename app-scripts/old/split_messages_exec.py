import re
import sys

# Header pattern and validity line pattern
header_pattern = re.compile(r'\*{4}(\d+)\*{4}')  # Header format: ****0000000195****
validity_pattern = re.compile(r'VALID_MSG:\s*(yes|no)')  # Custom line indicating validity

buffer = ""
for line in sys.stdin:
    buffer += line
    # Check for header pattern
    if header_pattern.search(line):
        if buffer.strip():
            # Check validity line in buffer
            if validity_pattern.search(buffer):
                valid = validity_pattern.search(buffer).group(1)
                status = "valid" if valid.lower() == "yes" else "invalid"
            else:
                status = "unknown"

            # Output each message with status
            print(f"---MESSAGE_START---\nStatus: {status}\n{buffer}\n---MESSAGE_END---")
        buffer = ""