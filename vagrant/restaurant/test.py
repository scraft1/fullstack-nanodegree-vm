import re

test = "this is a test5"
match = re.search(r"test\d$", test)
print match.group(0)
