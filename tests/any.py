from datetime import datetime


class Any:
    def __init__(self, klass: type) -> None:
        self.klass = klass

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.klass)

    def __hash__(self) -> int:
        return hash(self.klass)


class AnyTimestamp:
    def __eq__(self, o: object) -> bool:
        try:
            datetime.fromisoformat(o)
            return True
        except ValueError:
            return False
