from debian.debian_support import Version


def aNewerThanB(a: str, b: str):
    return Version(a.replace("_", "")) > Version(b.replace("_", ""))
