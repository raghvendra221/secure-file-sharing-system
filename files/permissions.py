def can_upload(user):
    return user.role in ["admin", "uploader"]


def can_download(user, file):
    if user.role == "admin":
        return True

    if file.owner == user:
        return True

    # Allow viewer (token validation already done)
    if user.role == "viewer":
        return True

    return False


def can_delete(user, file):
    if user.role == "admin":
        return True
    return user.role == "uploader" and file.owner == user


def can_generate_token(user, file):
    if user.role == "admin":
        return True
    return user.role == "uploader" and file.owner == user