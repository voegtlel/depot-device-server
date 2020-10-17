import time
from pydantic import BaseModel

from threading import Thread

from typing import Optional


class CardAuthConfig(BaseModel):
    server_url: str
    client_id: str
    card_login_api_key: Optional[str]
    card_associate_login_timeout: Optional[int]


class CardReader:
    config: CardAuthConfig
    _last_seen_id: Optional[bytes] = None
    _last_fetched_id: Optional[str] = None
    _last_seen_timestamp: float = 0
    _running: bool

    def __init__(self, config: CardAuthConfig):
        self.config = config
        self._reader_thread = Thread(target=self._read_card_thread, name="card_reader_thread")

    def start(self):
        self._running = True
        self._reader_thread.start()

    def stop(self):
        self._running = False
        self._reader_thread.join()

    def _read_card_thread(self):
        import nxppy
        mifare = nxppy.Mifare()

        while self._running:
            try:
                time.sleep(0.1)
                read_card_id = mifare.select()
            except nxppy.SelectError:
                read_card_id = None

            if time.time() - self._last_seen_timestamp > self.config.card_associate_login_timeout:
                # Reset last seen state if timeout occurred
                self._last_seen_id = None
                self._last_fetched_id = None
            if read_card_id is not None and self._last_seen_id != read_card_id:
                # Save the read card data if different
                self._last_seen_id = read_card_id
                self._last_fetched_id = read_card_id.hex()
                self._last_seen_timestamp = time.time()

    def read_card_id(self) -> str:
        """
        Returns and resets the last encountered card id. Should not return the same card twice within a specific time
        interval.

        Returns:
            The read card identifier (length is not defined, but it must be unique).
        """
        result = self._last_fetched_id
        self._last_fetched_id = None
        return result
