from enum import Enum


class Gender(str, Enum):
    unknown = "unknown"
    male = "male"
    female = "female"
