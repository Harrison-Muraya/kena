import datetime
import string
import secrets

# Starting prefix (adjust if your starting point is different)
START_PREFIX = "AAAA"
EPOCH_DATE = datetime.date(2024, 1, 1)

# Function to increment letters like base-26 counter
def increment_prefix(base_prefix, days_passed):
    chars = list(base_prefix)
    for _ in range(days_passed):
        i = len(chars) - 1
        while i >= 0:
            if chars[i] == 'Z':
                chars[i] = 'A'
                i -= 1
            else:
                chars[i] = chr(ord(chars[i]) + 1)
                break
    return ''.join(chars)

# For uniqueness, you may store previously used suffixes in a DB or in memory
used_suffixes = set()

def generate_unique_suffix(length=6):
    while True:
        # Generates a secure random alphanumeric string
        suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))
        if suffix not in used_suffixes:
            used_suffixes.add(suffix)
            return suffix

# Full code generator
def generate_code():
    today = datetime.date.today()
    days_passed = (today - EPOCH_DATE).days
    prefix = increment_prefix(START_PREFIX, days_passed)
    suffix = generate_unique_suffix()
    return prefix + suffix
