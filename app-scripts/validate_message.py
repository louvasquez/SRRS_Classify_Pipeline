import sys

c = bytes.fromhex("0a")[0]
msg_and_head = sys.stdin.read()
head = int(msg_and_head.splitlines(c)[0][4:-5]) # get size from 1st line ****ssssssssss****
msg = '\n'.join(msg_and_head.split('\n')[1:])
if head == len(msg):
    print(f"CHECKING: {head} against real {len(msg)}")
    print(msg)
else:
    print("FAIL_HEADER_CHECK")
    print(msg_and_head)