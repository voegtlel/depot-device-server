from typing import Optional


class CardAccessMock:

    def __init__(self):
        self.card_id: Optional[str] = None

    def insert_card(self, card_id: Optional[str]):
        self.card_id = card_id

    def get_card_id(self) -> Optional[str]:
        return self.card_id


class CardAccessFileMock:

    def get_card_id(self) -> Optional[str]:
        with open('mock-card.txt') as cardf:
            data = cardf.readline()
            if data:
                return data
        return None


class BayAccessMock:

    def __init__(self):
        self.bays = {
            'bay1': False,
            'bay2': False,
        }

    def has_bay(self, bay_id: str) -> bool:
        return bay_id in self.bays

    def is_bay_open(self, bay_id: str):
        return self.bays.get(bay_id, False)

    def open_bay(self, bay_id: str):
        self.bays[bay_id] = True
        from threading import Thread
        Thread(target=self._close_bay_after, args=[bay_id], daemon=True).start()

    def _close_bay_after(self, bay_id: str):
        import time
        time.sleep(10.0)
        self.close_bay_mock(bay_id)

    def close_bay_mock(self, bay_id: str):
        self.bays[bay_id] = False
