# Error handling
class MoveError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class HighSoftStruck(MoveError):
    def __init__(self, Position):
        value = f"{Position} is outside the High Soft limit for this Axis."
        super().__init__(value)

class LowSoftStruck(MoveError):
    def __init__(self, Position):
        value = f"{Position} is outside the Low Soft limit for this Axis."
        super().__init__(value)

class Overspeed(MoveError):
    def __init__(self, Speed):
        value = f"The speed '{Speed}' is too fast for this axis.'"
        super().__init__(value)

class Underspeed(MoveError):
    def __init__(self, Speed):
        value = f"The speed '{Speed}' is too slow for this axis."
        super().__init__(value)
