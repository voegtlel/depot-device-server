import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from fastapi import APIRouter
from typing import List, Optional

from device_server.bay.station import Station
from device_server.config import config
from device_server.model import BayState

router = APIRouter()


station: Optional[Station] = None
thread_executor = ThreadPoolExecutor(1, thread_name_prefix="hardware_thread_")


async def bay_startup():
    global station
    assert station is None, "Already initialized"
    station = Station(config.station)
    await asyncio.get_running_loop().run_in_executor(thread_executor, station.configure)


async def bay_shutdown():
    global station
    assert station is not None, "Not initialized"
    station = None


@router.get(
    '/bays',
    tags=['Bay'],
    response_model=List[BayState],
)
async def get_bays() -> List[BayState]:
    return [
        BayState(id=bay_id, open=is_open)
        for bay_id, is_open in
        (await asyncio.get_running_loop().run_in_executor(thread_executor, station.get_states)).items()
    ]


@router.get(
    '/bays/{bay_id}',
    tags=['Bay'],
    response_model=BayState,
)
async def get_bay(bay_id: str) -> BayState:
    return BayState(
        id=bay_id, open=await asyncio.get_running_loop().run_in_executor(thread_executor, station.get_state, bay_id)
    )


@router.post(
    '/bays/open',
    tags=['Bay'],
)
async def open_all_bays() -> None:
    await asyncio.get_running_loop().run_in_executor(thread_executor, station.open_all_bays)


@router.post(
    '/bays/{bay_id}/open',
    tags=['Bay'],
)
async def open_bay(bay_id: str) -> None:
    await asyncio.get_running_loop().run_in_executor(thread_executor, station.open_bay, bay_id)
