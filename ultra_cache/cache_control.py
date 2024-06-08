from typing import Union
import sys

if sys.version_info[0] == 3 and sys.version_info[1] >= 11:
    from typing import Self
else:
    from typing_extensions import Self


class CacheControl:
    REQUEST_ONLY_KEYS = ["max-stale", "min-fresh", "only-if-cached"]

    def __init__(self, parts: dict[str, str]) -> None:
        self.parts: dict[str, Union[str, None]] = parts

    def set(self, key: str, value: str) -> None:
        self.parts[key] = value

    def get(self, key: str) -> Union[str, None]:
        return self.parts.get(key, None)

    def setdefault(self, key: str, value: str) -> None:
        self.parts.setdefault(key, value)

    @classmethod
    def from_string(cls, cache_control: Union[str, None]) -> Self:
        if cache_control is None:
            return cls({})
        return cls(
            {
                x.split("=")[0].strip(): x.split("=")[1].strip() if "=" in x else None
                for x in cache_control.lower().split(",")
            }
        )

    @property
    def max_age(self) -> Union[int, None]:
        value = self.parts.get("max-age", None)
        if value is None:
            return None
        return int(value)

    @property
    def no_cache(self) -> bool:
        return "no-cache" in self.parts

    @property
    def no_store(self) -> bool:
        return "no-store" in self.parts

    def to_response_header(self) -> str:
        return ", ".join(
            [
                f"{k}={v}"
                for k, v in self.parts.items()
                if k not in self.REQUEST_ONLY_KEYS
            ]
        )
