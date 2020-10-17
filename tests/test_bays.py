from fastapi.testclient import TestClient
from typing import Dict, Tuple, List

import device_server.bay.controller
import smbus
from device_server.api import app
from device_server.model import BayState


class WriteListener:
    def __init__(self):
        self.writes: List[Tuple[float, int, int, int, int]] = []
        self.time: float = 0.0

    def sleep(self, delay: float):
        self.time += delay

    def __call__(self, port: int, address: int, register: int, data: int) -> int:
        self.writes.append((self.time, port, address, register, data))
        return data


def _count_bits(i: int):
    i = i - ((i >> 1) & 0x55555555)
    i = (i & 0x33333333) + ((i >> 2) & 0x33333333)
    return (((i + (i >> 4) & 0xF0F0F0F) * 0x1010101) & 0xffffffff) >> 24


def test_bay(monkeypatch):
    write_listener = WriteListener()
    monkeypatch.setattr(smbus.SMBus, '_write_listener', write_listener)
    monkeypatch.setattr(device_server.bay.controller, 'sleep', write_listener.sleep)

    with TestClient(app) as client:
        write_listener.writes.clear()

        smbus.SMBus._state['1.32.0'] = 0xff
        smbus.SMBus._state['1.32.1'] = 0xff
        smbus.SMBus._state['1.33.0'] = 0xff

        resp = client.get('/api/v1/device/bays')
        assert resp.status_code == 200, resp.text
        bay_states = [BayState.validate(r) for r in resp.json()]
        assert bay_states == [
            BayState(id='1A', open=False),
            BayState(id='2A', open=False),
            BayState(id='3A', open=False),
            BayState(id='4A', open=False),
            BayState(id='5A', open=False),
            BayState(id='1B', open=False),
            BayState(id='2B', open=False),
            BayState(id='3B', open=False),
            BayState(id='4B', open=False),
            BayState(id='5B', open=False),
            BayState(id='6B', open=False),
            BayState(id='1C', open=False),
            BayState(id='2C', open=False),
            BayState(id='4C', open=False),
            BayState(id='5C', open=False),
            BayState(id='6C', open=False),
            BayState(id='7C', open=False),
            BayState(id='1D', open=False),
            BayState(id='2D', open=False),
            BayState(id='3D', open=False),
            BayState(id='4D', open=False),
            BayState(id='5D', open=False),
            BayState(id='6D', open=False),
            BayState(id='7D', open=False),
        ]

        smbus.SMBus._state['1.32.0'] = 0xaa
        smbus.SMBus._state['1.32.1'] = 0xaa
        smbus.SMBus._state['1.33.0'] = 0xaa

        resp = client.get('/api/v1/device/bays')
        assert resp.status_code == 200, resp.text
        bay_states = [BayState.validate(r) for r in resp.json()]
        assert bay_states == [
            BayState(id='1A', open=False),
            BayState(id='2A', open=True),
            BayState(id='3A', open=False),
            BayState(id='4A', open=True),
            BayState(id='5A', open=False),
            BayState(id='1B', open=True),
            BayState(id='2B', open=False),
            BayState(id='3B', open=True),
            BayState(id='4B', open=False),
            BayState(id='5B', open=True),
            BayState(id='6B', open=False),
            BayState(id='1C', open=True),
            BayState(id='2C', open=False),
            BayState(id='4C', open=True),
            BayState(id='5C', open=False),
            BayState(id='6C', open=True),
            BayState(id='7C', open=True),
            BayState(id='1D', open=False),
            BayState(id='2D', open=True),
            BayState(id='3D', open=False),
            BayState(id='4D', open=True),
            BayState(id='5D', open=False),
            BayState(id='6D', open=True),
            BayState(id='7D', open=False),
        ]

        for bay_state in bay_states:
            resp = client.get(f'/api/v1/device/bays/{bay_state.id}')
            assert resp.status_code == 200, resp.text
            bay_state_cmp = BayState.validate(resp.json())
            assert bay_state_cmp == bay_state

        assert write_listener.writes == []

        resp = client.post(f'/api/v1/device/bays/1A/open')
        assert resp.status_code == 200, resp.text
        assert write_listener.writes == [
            (0.0, 1, 0x22, 0x00, 0x00),
            (0.0, 1, 0x22, 0x01, 0x00),
            (0.01, 1, 0x22, 0x01, 0x80),
            (0.02, 1, 0x22, 0x01, 0x00),
        ]

        write_listener.writes.clear()
        write_listener.time = 0.0

        resp = client.post(f'/api/v1/device/bays/7D/open')
        assert resp.status_code == 200, resp.text
        assert write_listener.writes == [
            (0.0, 1, 0x23, 0x00, 0x00),
            (0.0, 1, 0x23, 0x01, 0x00),
            (0.01, 1, 0x23, 0x00, 0x80),
            (0.02, 1, 0x23, 0x00, 0x00),
        ]

        write_listener.writes.clear()
        write_listener.time = 0.0

        resp = client.post(f'/api/v1/device/bays/open')
        assert resp.status_code == 200, resp.text
        assert len(write_listener.writes) == 4 * len(bay_states)
        # Check every position in the state
        last_state: Dict[Tuple[int, int, int], int] = {
            (1, 0x22, 0x00): 0x00,
            (1, 0x22, 0x01): 0x00,
            (1, 0x23, 0x00): 0x00,
            (1, 0x23, 0x01): 0x00,
        }
        current_time = 0.0
        state = last_state.copy()
        # Check that there is at every point in time never more than 1 bit enabled (including bits which are being set
        # at the "same" point in time)
        for write in write_listener.writes:
            if current_time != write[0]:
                current_time = write[0]
                state = last_state.copy()
            last_state[write[1:4]] = write[4]
            state[write[1:4]] |= write[4]
            bitcount = 0
            for i, st in state.items():
                bitcount += _count_bits(st)
            assert bitcount in (0, 1)
