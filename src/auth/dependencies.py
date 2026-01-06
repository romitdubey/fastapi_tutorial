from fastapi.security import HTTPBearer
from fastapi import Request,status, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_access_token
from fastapi.exceptions import HTTPException
from src.db.redis import jti_in_blocklist
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import UserService

user_service = UserService()
class TokenBearer(HTTPBearer):
    def __init__(self, auto_error= True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request:Request)-> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request) 
        token = creds.credentials
        token_data = decode_access_token(token)
        
        if not self.validate_token(token):
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Invalid or expired token."
            )

        if await jti_in_blocklist(token_data['jti']):
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Token has been revoked."
            )
        self.verify_token_data(token_data)
        return token_data

    def validate_token(self, token:str)-> bool:
        token_data = decode_access_token(token)
        if token_data is None:
            return False
        return True

    def verify_token_data(self, token_data:dict) -> None:
        raise NotImplementedError("Please Overide this method in subclass.")


class AcessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict) -> None:
        if token_data and token_data['refresh']:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "please use access token only."
            )

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict) -> None:
        if token_data and not token_data['refresh']:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "please provide a refresh token."
            )

async def get_current_user(
    token_details:dict=Depends(AcessTokenBearer()),
    session:AsyncSession = Depends(get_session)
    ):
    user_email = token_details['user']['email']

    user = await user_service.get_user(user_email,session=session)

    return user