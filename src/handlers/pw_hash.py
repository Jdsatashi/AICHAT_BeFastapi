from src.conf.settings import PWD_CONTEXT


def hash_pass(password: str):
    return PWD_CONTEXT.hash(password)


def verify_password(plain_password: str, hashed_password) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)
