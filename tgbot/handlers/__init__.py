"""Import all routers and add them to routers_list."""
from tgbot.handlers.user import user_routers_list

routers_list = [
    user_routers_list,
]

__all__ = [
    "routers_list",
]
