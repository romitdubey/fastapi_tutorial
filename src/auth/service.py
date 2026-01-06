from .models import User
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import UserCreateModel
from .utils import hash_password
from sqlmodel import select 
import logging 


class UserService:
    async def get_user(self, email:str, session:AsyncSession) -> User | None:
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        return result.first()

    async def user_exists(self, email:str, session:AsyncSession) -> bool:
        user = await self.get_user(email, session)
        return user is not None

    async def create_user(self, user_data:UserCreateModel, session:AsyncSession) -> User:
        user_data_dict = user_data.model_dump()
        password_hash = hash_password(user_data_dict["password"])
        new_user = User(**user_data_dict)
        new_user.password_hash = password_hash
        session.add(new_user)
        await session.commit()
        return new_user