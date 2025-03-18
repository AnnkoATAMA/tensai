from schemas import user as user_schema
from db import get_db
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
import cruds.user as user_crud

user_router = APIRouter()


@user_router.post("/user/register", response_model=user_schema.UserCreateResponse)
async def register(user_body: user_schema.UserCreate, db: AsyncSession = Depends(get_db)):
        
    return await user_crud.register(user_body, db)

@user_router.post("/user/login", response_model=user_schema.Token)
async def login_for_access_token(
    response: Response,
    form_data: user_schema.EmailPasswordLogin,
    db: AsyncSession = Depends(get_db)
):
    token_data = await user_crud.login_user(
        db=db,
        form_data=form_data,
        response=response
    )
    
    return user_schema.Token(**token_data)