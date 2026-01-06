from fastapi import APIRouter, Depends,status
from .schemas import UserCreateModel, UserModel, UserLoginModel
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import create_access_tokens, decode_access_token, verify_password
from datetime import timedelta
from fastapi.responses import JSONResponse
import logging
from .dependencies import RefreshTokenBearer, AcessTokenBearer, get_current_user
from src.db.redis import add_jti_to_blocklist
import datetime

auth_router = APIRouter() 

user_service = UserService()

REFRESH_TOKEN_EXPIRY = 2

@auth_router.post("/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email

    user_exists = await user_service.user_exists(email=email, session=session)
    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with this email already exists.")
    new_user = await user_service.create_user(user_data=user_data, session=session)

    return new_user

@auth_router.post("/login")
async def login_user(login_data:UserLoginModel, session: AsyncSession=Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user(email=email, session=session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)
        logging.info(f"Password valid: {password_valid}")
        if password_valid:
            user_data = {
                "user_id": str(user.uid),
                "email": str(user.email),
            }
            access_token = create_access_tokens(user_data=user_data)
            refresh_token = create_access_tokens(user_data=user_data, refesh=True, expiry=timedelta(days=REFRESH_TOKEN_EXPIRY))


            return JSONResponse(
                content={
                    "message":"Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user":{
                        "user_id": str(user.uid),
                        "email": str(user.email),
                    }
                }
            )
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

@auth_router.get("/refresh-token")
async def refresh_access_token(token_details:dict = Depends(RefreshTokenBearer())):
    expiry = token_details['exp']
    
    if datetime.datetime.fromtimestamp (expiry) > datetime.datetime.now():
        new_acess_token = create_access_tokens(
            user_data=token_details['user']
        )
        return JSONResponse(
            content={
                "access_token": new_acess_token
            }
            
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Refresh token expired. Please login again."
    )



@auth_router.get('/me')
async def get_current_user(user = Depends(get_current_user)):
    return user

@auth_router.get("/logout")
async def revoke_token(token_details:dict = Depends(AcessTokenBearer())):
    jti = token_details['jti']
    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={
            "message":"Logged out successfully."
        },
        status_code=status.HTTP_200_OK)