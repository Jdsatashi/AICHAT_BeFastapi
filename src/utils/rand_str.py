import random
import string


def random_string(length: int = 8) -> str:
    """Generate a random string of fixed length."""
    if length <= 0:
        length = 8

    # Generate a random string using letters and digits
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
   