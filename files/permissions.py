def can_upload(user):
    return user.role in ["admin", "uploader"]


def can_download(user, file):
    if user.role == "admin":
        return True
    return file.owner == user


def can_delete(user, file):
    if user.role == "admin":
        return True
    return user.role == "uploader" and file.owner == user


def can_generate_token(user, file):
    if user.role == "admin":
        return True
    return user.role == "uploader" and file.owner == user