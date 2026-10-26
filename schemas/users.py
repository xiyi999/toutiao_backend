from pydantic import BaseModel, ConfigDict, Field


class UserRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=2, max_length=72)


class UserInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str | None = None
    avatar: str | None = None
    gender: str | None = None
    bio: str | None = None


class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(alias="userInfo")

    model_config = ConfigDict(populate_by_name=True)


class UserUpdateRequest(BaseModel):
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone : str = None

    model_config = ConfigDict(populate_by_name=True)


class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(...,alias="oldPassword",description="旧密码")
    new_password: str = Field(...,alias="newPassword",description="新密码",min_length=6)

