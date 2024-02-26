import random
import string


def generator_password(length: int = 8) -> str:
    letters = string.ascii_letters
    digits = string.digits
    password = "".join(random.choice(letters + digits) for _ in range(length))

    return password
