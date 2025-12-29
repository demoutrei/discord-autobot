from enum import auto, StrEnum


class TriggerType(StrEnum):
  keyword: str = auto()
  regex: str = auto()