_aws_region = "us-east-1"


def get():
    return _aws_region


def set(region_name):
    global _aws_region
    _aws_region = region_name
