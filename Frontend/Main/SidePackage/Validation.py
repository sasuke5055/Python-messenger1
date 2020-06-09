minimum_pass_len = 8


def validate_email(text):
    if len(text) < 7:
        return False
    if not text.__contains__('@'):
        return False
    at_index = text.rfind('@')
    if (at_index == -1) or (not text[at_index + 2:].__contains__('.')):
        return False
    if text[0] == '@' or text[len(text) - 1] == '@':
        return False

    # Another conditions

    # If all conditions passed
    return True


def validate_password(text):
    if len(text) < minimum_pass_len:
        return False
    # Another conditions

    # If all conditions passed
    return True
