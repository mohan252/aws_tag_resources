_aws_profile = "default"


def get():
    return _aws_profile


def set(profile):
    global _aws_profile
    _aws_profile = profile