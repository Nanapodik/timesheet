import bcrypt


def hash_password(password: str) -> str:
    """
    Хеширует пароль с использованием bcrypt.
    """
    password_bytes = password.encode("utf-8")

    password_hash = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return password_hash.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Проверяет обычный пароль относительно сохранённого хеша.
    """
    password_bytes = plain_password.encode("utf-8")
    hash_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(
        password_bytes,
        hash_bytes,
    )