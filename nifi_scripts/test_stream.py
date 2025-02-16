import re
import sys

header_pattern = re.compile(r'\*{4}(\d+)\*{4}')  # Header format: ****0000000195****

for line in sys.stdin.buffer:
    try:
        decoded_line = line.decode('utf-8').strip()
        if header_pattern.search(decoded_line):
            print(decoded_line)
    except UnicodeDecodeError:
        decoded_line = line.decode('latin-1').strip()  # Fallback decoding
        print("DECODE_ERROR: "+decoded_line)

