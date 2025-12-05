import os
import re
from typing import List, Tuple, TypedDict

class ParsedFrontendBaseUrl(TypedDict):
    id: str
    base_url: str
    is_enabled: bool

# WARNING: THIS HAS BEEN VIBE-CODED, DIDN"T TEST IT TOO STRICKTLY
def get_frontend_base_urls(prefix: str = "FRONTEND_BASE_URL") -> List[ParsedFrontendBaseUrl]:
    """
    Collect all environment variables that start with the given prefix
    (e.g. FRONTEND_BASE_URL, FRONTEND_BASE_URL_2, FRONTEND_BASE_URL_3, ...)
    and return their values as a list of URLs.

    The variables are sorted by their numeric suffix, with the unsuffixed
    one (FRONTEND_BASE_URL) coming first.
    """
    pattern = re.compile(rf"^{re.escape(prefix)}(?:_(\d+))?$")

    items: list[Tuple[int,ParsedFrontendBaseUrl]] = []
    for key, value in os.environ.items():
        match = pattern.match(key)
        if match:
            # If there’s a numeric suffix, use it; otherwise treat as 0
            suffix = match.group(1)
            index = int(suffix) if suffix is not None else 0
            split = value.split('|')
            parsed = ParsedFrontendBaseUrl(
                id=split[1],
                base_url=split[0],
                is_enabled=split[2] == 'true'
            )
            items.append((index, parsed))

    # Sort by numeric suffix and return just the URL values
    items.sort(key=lambda x: x[0])
    return [value for _, value in items]


print(get_frontend_base_urls())