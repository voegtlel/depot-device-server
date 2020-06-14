from typing import Optional


class CardAccess:
    # TODO(@felix): Implement this

    def __init__(self):
        pass

    def get_card_id(self) -> Optional[str]:
        # TODO(@felix): Implement this
        return None


class BayAccess:
    # TODO(@felix): Implement this

    def __init__(self):
        pass

    def has_bay(self, bay_id: str) -> bool:
        return True

    def is_bay_open(self, bay_id: str) -> bool:
        return False

    def open_bay(self, bay_id: str):
        pass

