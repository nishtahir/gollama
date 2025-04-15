import math
import os

__PROJECT_ROOT__ = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


def human_readable_size(size: float, precision: int = 2) -> str:
    if size == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, precision)
    return "%s %s" % (s, size_name[i])
