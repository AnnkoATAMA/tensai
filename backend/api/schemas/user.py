from pydantic import BaseModel, Field, ConfigDict

# basic infomation of user
class UserBase(BaseModel):
    name: str = Field(..., title="ユーザ名")
    email: str = Field(..., title="メールアドレス")
    
# return token
class Token(BaseModel):
    access_token: str
    token_type: str
    
# login with email and password
class EmailPasswordLogin(BaseModel):
    email: str = Field(..., title="メールアドレス")
    password: str = Field(..., title="パスワード")

# user create
class UserCreate(UserBase):
    password: str = Field(..., title="パスワード")

# return user infomation
class UserCreateResponse(UserBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
    
