from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from .bay import router as bays_router, bay_startup, bay_shutdown
from .auth import router as auth_router, card_startup, card_shutdown
from device_server.config import config

router = APIRouter()
router.include_router(bays_router, prefix='/api/v1/device')
router.include_router(auth_router, prefix='/api/v1/auth')


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allow_origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allow_headers=['*'],
)

app.include_router(router)
