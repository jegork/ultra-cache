import sys
from datetime import datetime

if sys.version_info[0] == 3 and sys.version_info[1] >= 11:
    from datetime import UTC
else:
    UTC = None


def utc_now():
    if UTC is None:
        return datetime.utcnow()
    else:
        return datetime.now(UTC)
