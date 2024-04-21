from datetime import datetime, timedelta
from typing import List

from sqlalchemy import select, and_, desc, delete

from infrastructure.database.models import Message, MessageStatistic
from infrastructure.database.repo.base import BaseRepo


class MessageRepo(BaseRepo):
    async def get_messages(self, session_id: str) -> List[Message]:
        stmt = select(
            Message
        ).where(
            Message.session_id == session_id,
        ).order_by(
            desc(Message.id)
        ).limit(12)
        result = await self.session.execute(stmt)
        messages = result.scalars().all()
        sorted_messages = sorted(messages, key=lambda message: message.id)
        return sorted_messages

    async def clear_messages(self, session_id: str):
        smt = delete(
            Message
        ).where(
            Message.session_id == session_id,
        )
        await self.session.execute(smt)
        await self.session.commit()

    async def clear_chats_inactive_users(self):
        cutoff_time = datetime.utcnow() - timedelta(minutes=15)
        stmt = (
            select(MessageStatistic)
            .join(Message, MessageStatistic.user_id == Message.session_id)
            .where(MessageStatistic.last_message_time < cutoff_time)
            .distinct(MessageStatistic.user_id)
        )

        result = await self.session.execute(stmt)
        users = result.scalars().all()
        for user in users:
            stmt = (
                delete(Message)
                .where(Message.session_id == user.user_id)
            )
            await self.session.execute(stmt)
        await self.session.commit()
