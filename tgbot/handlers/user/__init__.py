from tgbot.handlers.user.consultation import consultation_router
from tgbot.handlers.user.start import start_router

user_routers_list = [
    start_router,
    consultation_router
]

__all__ = [
    "user_routers_list",
]