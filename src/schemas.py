import enum
from datetime import datetime

from pydantic import BaseModel, HttpUrl, ConfigDict

class PromptTypeEnum(str, enum.Enum):
    static = 'static'
    dynamic = 'dynamic'

class ButtonTypeEnum(str, enum.Enum):
    static = 'static'
    dynamic = 'dynamic'


class KbButtonSchema(BaseModel):
    id: int
    name: str
    url: HttpUrl
    type: ButtonTypeEnum


class UserSchema(BaseModel):
    id: int
    full_name: str
    created_at: datetime


class WelcomeMessageSchema(BaseModel):
    id: int
    text: str


class SettingsSchema(BaseModel):
    id: int
    dynamic_button_count: int
    welcome_message: str

class SoundSchema(BaseModel):
    id: int
    name: str
    file_data: bytes

    model_config = ConfigDict(from_attributes=True)