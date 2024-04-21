import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from infrastructure.database.models import User, MessageStatistic
from infrastructure.database.repo.base import BaseRepo


class UserRepo(BaseRepo):

    async def get_user(self,
                       user_id: str = None,
                       telegram_id: int = None,
                       username: str = None) -> User:
        smt = select(User).options(
            selectinload(User.message_statistic),
        )

        if user_id:
            smt = smt.where(User.id == user_id)
        if telegram_id:
            smt = smt.where(User.telegram_id == telegram_id)
        if username:
            smt = smt.where(User.username == username)

        result = await self.session.execute(smt)
        return result.scalar()

    async def get_or_create_user(
        self,
        telegram_id: int,
        full_name: str,
        username: Optional[str] = None,
    ):
        insert_stmt = select(User).from_statement(
            insert(User)
            .values(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name,
            )
            .returning(User)
            .on_conflict_do_update(
                index_elements=[User.telegram_id],
                set_=dict(
                    username=username,
                    full_name=full_name,
                ),
            )
        )
        result = await self.session.scalars(insert_stmt)

        await self.session.commit()
        return result.first()

    async def track_messages_to_ai(self, user_id: str):
        user = await self.get_user(user_id)
        current_time = datetime.datetime.utcnow()
        if user.message_statistic:
            statistic = user.message_statistic
            if not statistic.last_message_time:
                user.last_message_time = datetime.datetime.utcnow()

            if statistic.last_message_time.date() == current_time.date():
                statistic.messages_today += 1

                if statistic.last_message_time.time().hour == current_time.time().hour:
                    statistic.messages_hour += 1
                else:
                    statistic.messages_hour = 1
            else:
                statistic.messages_today = 1
                statistic.messages_hour = 1
            statistic.messages_total += 1

            statistic.last_message_time = current_time
        else:
            self.session.add(MessageStatistic(
                user_id=user.id,
                messages_today=1,
                messages_hour=1,
                messages_total=1,
                last_message_time=current_time
            ))

        await self.session.commit()
