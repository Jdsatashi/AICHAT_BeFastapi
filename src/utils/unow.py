from datetime import datetime
from src.conf.settings import VN_TZ

"""
    A function to get the current time in Vietnam timezone.
    If `aware` is True, it returns an aware datetime object.
"""
def now_vn(aware = False):
    result = datetime.now(VN_TZ)
    if aware:
        return result
    else:
        return result.replace(tzinfo=None)
