from typing import Dict


class FormValidationError(ValueError):
    def __init__(self, errors: Dict[str, str]) -> None:
        self.errors = errors

    def has(self, name):
        return self.errors.get(name, None) is not None

    def msg(self, name):
        return self.errors.get(name, None)
