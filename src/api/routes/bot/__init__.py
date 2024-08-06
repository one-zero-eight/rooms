from fastapi import APIRouter

from src.api.auth.utils import BOT_ACCESS_DEPENDENCY
from .invitation import router as invitation_router
from .order import router as order_router
from .room import router as room_router
from .rule import router as rule_router
from .task import router as task_router
from .user import router as user_router

bot_router = APIRouter(prefix="/bot", dependencies=[BOT_ACCESS_DEPENDENCY])

bot_router.include_router(user_router)
bot_router.include_router(room_router)
bot_router.include_router(task_router)
bot_router.include_router(order_router)
bot_router.include_router(invitation_router)
bot_router.include_router(rule_router)
